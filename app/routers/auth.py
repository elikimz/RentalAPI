from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app import models, schemas, database, utils

router = APIRouter()

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Function to get a user by email
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# Function to check if the first user (for Admin role)
def is_first_user(db: Session):
    return db.query(models.User).count() == 0

# Function to authenticate a user by checking their email and password
def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not utils.verify_password(password, user.password):
        return None
    return user

# Route to register a new user
@router.post("/register", response_model=schemas.UserResponse)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Check if email already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Assign role: Admin for the first user, Tenant for others
    role = "Admin" if is_first_user(db) else "Tenant"
    
    # Hash the user's password
    hashed_password = utils.hash_password(user_data.password)
    
    # Create the new user object
    new_user = models.User(
        full_name=user_data.full_name,
        email=user_data.email,
        password=hashed_password,
        role=role,  # Set role based on first user check
        is_active=True
    )
    
    # Add user to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # ✅ If the user is a Tenant, also create a Tenant entry
    if role == "Tenant":
        new_tenant = models.Tenant(
            user_id=new_user.id,  # Link Tenant to the User
            full_name=new_user.full_name,
            email=new_user.email,
            phone_number=user_data.phone_number  # Ensure `phone_number` is added to UserCreate schema
        )
        db.add(new_tenant)
        db.commit()
        db.refresh(new_tenant)

    return new_user


# Route to login and generate an access token
@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # Authenticate the user
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create an access token with a 30-minute expiry time
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}

# Helper function to get the current logged-in user based on the token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Fetch user from the database
    user = get_user_by_email(db, email)
    
    if user is None:
        raise credentials_exception
    
    return user

# Role-based access control: Only allow certain roles to access specific resources
def require_role(allowed_roles: list):
    def role_dependency(current_user: models.User = Depends(get_current_user)):
        # Check if the user's role is in the allowed roles list (case-insensitive check)
        if current_user.role.lower() not in [role.lower() for role in allowed_roles]:
            raise HTTPException(status_code=403, detail="You do not have permission to access this resource")
        return current_user
    return role_dependency

# Route to get the current user's information
@router.get("/me", response_model=schemas.UserResponse)
def get_user_info(current_user: models.User = Depends(get_current_user)):
    return schemas.UserResponse.from_orm(current_user)