# Python
import json
from uuid import UUID
from datetime import date, datetime
from typing import Optional, List

# Pydantic
from pydantic import BaseModel, EmailStr, Field

# FastAPI
from fastapi import FastAPI, status, Body, HTTPException, Path

app = FastAPI()

# Models

class PasswordMixin(BaseModel):
    password: str = Field(
        ...,
        min_length=8,
        max_length=64,
        example="password",
    )


class UserBase(BaseModel):
    user_id : UUID = Field(...)
    email : EmailStr = Field(...)


class User(UserBase):
    first_name : str = Field(
        ...,
        min_length=1,
        max_length=50,
    )
    last_name : str = Field(
        ...,
        min_length=1,
        max_length=50,
    )
    birth_date : Optional[date] = Field(default=None)



class UserRegister(PasswordMixin, User):
    pass


class UserLogin(PasswordMixin, UserBase):
    pass


class Tweet(BaseModel):
    tweet_id : UUID = Field(...)
    user_id : UUID = Field(...)
    content : str = Field(
        ...,
        min_length=1,
        max_length=256,
    )
    created_at: datetime = Field(default=datetime.now())
    updated_at : Optional[datetime] = Field(default=None)


# Routes

@app.get(
    path="/",
)
def home():
    return {"message": "Hello World"}

## Users

### Register a new user
@app.post(
    path="/signup",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Sign up a new user",
    tags=["Users"],
)
def signup(user: UserRegister = Body(...)):
    """
    Sign up a new user

    This endpoint allows you to sign up a new user.

    Parameters:
    - Request body:
        - user: UserRegister

    Returns:
    - User: The newly created user with the following fields:
        - user_id: UUID
        - email: EmailStr
        - first_name: str
        - last_name: str
        - birth_date: Optional[date]
    """
    with open("users.json", "r+", encoding="utf-8") as f:
        users = json.loads(f.read())
        user_dict = user.dict()
        user_dict["user_id"] = str(user_dict["user_id"])
        user_dict["birth_date"] = str(user_dict["birth_date"])
        users.append(user_dict)
        f.seek(0)
        f.write(json.dumps(users, indent=4))
        return user


### Login a user
@app.post(
    path="/login",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Login a user",
    tags=["Users"],
)
def login(user: UserLogin = Body(...)):
    """
    Login a user

    This endpoint allows you to login a user.

    Parameters:
    - Request body:
        - user: UserLogin

    Returns:
    - User: The logged in user with the following fields:
        - user_id: UUID
        - email: EmailStr
        - first_name: str
        - last_name: str
        - birth_date: Optional[date]
    """
    with open("users.json", "r+", encoding="utf-8") as f:
        users = json.loads(f.read())
        for user_dict in users:
            if user_dict["email"] == user.email and user_dict["password"] == user.password:
                return User(**user_dict)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

### Get all users
@app.get(
    path="/users/",
    response_model=List[User],
    status_code=status.HTTP_200_OK,
    summary="Get all users",
    tags=["Users"],
)
def get_users():
    """
    Get all users

    This endpoint allows you to get all users.

    Returns:
    - List[User]: A list of all users with the following fields:
        - user_id: UUID
        - email: EmailStr
        - first_name: str
        - last_name: str
        - birth_date: Optional[date]
    """
    with open("users.json", "r", encoding="utf-8") as f:
        users = json.loads(f.read())
        return [User(**user) for user in users]

### Get a user
@app.get(
    path="/users/{user_id}",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Get a user",
    tags=["Users"],
)
def get_user(user_id: UUID = Path(...)):
    """
    Get a user

    This endpoint allows you to get a user.

    Parameters:
    - Path parameters:
        - user_id: UUID

    Returns:
    - User: The user with the following fields:
        - user_id: UUID
        - email: EmailStr
        - first_name: str
        - last_name: str
        - birth_date: Optional[date]
    """
    with open("users.json", "r", encoding="utf-8") as f:
        users = json.loads(f.read())
        for user_dict in users:
            if user_dict["user_id"] == str(user_id):
                return User(**user_dict)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

### Update a user
@app.put(
    path="/users/{user_id}",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Update a user",
    tags=["Users"],
)
def update_user(user_id: UUID = Path(...), user: User = Body(...)):
    """
    Update a user

    This endpoint allows you to update a user.

    Parameters:
    - Path parameters:
        - user_id: UUID
    - Request body:
        - user: User

    Returns:
    - User: The updated user with the following fields:
        - user_id: UUID
        - email: EmailStr
        - first_name: str
        - last_name: str
        - birth_date: Optional[date]
    """
    with open("users.json", "r+", encoding="utf-8") as f:
        users = json.loads(f.read())
        for user_dict in users:
            if user_dict["user_id"] == str(user_id):
                user_dict.update(user.dict())
                user_dict["user_id"] = str(user_id)
                user_dict["birth_date"] = str(user_dict["birth_date"])
                f.seek(0)
                f.write(json.dumps(users, indent=4))
                return User(**user_dict)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

### Delete a user
@app.delete(
    path="/users/{user_id}",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Delete a user",
    tags=["Users"],
)
def delete_user(user_id: UUID = Path(...)):
    """
    Delete a user

    This endpoint allows you to delete a user.

    Parameters:
    - Path parameters:
        - user_id: UUID

    Returns:
    - User: The deleted user with the following fields:
        - user_id: UUID
        - email: EmailStr
        - first_name: str
        - last_name: str
        - birth_date: Optional[date]
    """
    f = open("users.json", "r", encoding="utf-8")
    users = json.loads(f.read())
    for user_dict in users:
        if user_dict["user_id"] == str(user_id):
            users.remove(user_dict)
            f.close()
            f = open("users.json", "w", encoding="utf-8")
            f.write(json.dumps(users, indent=4))
            f.close()
            return User(**user_dict)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


## Tweets

### Get all tweets
@app.get(
    path="/tweets/",
    response_model=List[Tweet],
    status_code=status.HTTP_200_OK,
    summary="Get all tweets",
    tags=["Tweets"],
)
def get_tweets():
    """
    Get all tweets

    This endpoint allows you to get all tweets.

    Returns:
    - List[Tweet]: A list of all tweets with the following fields:
        - tweet_id: UUID
        - user_id: UUID
        - content: str
        - created_at: datetime
        - updated_at: Optional[datetime]
    """
    with open("tweets.json", "r", encoding="utf-8") as f:
        tweets = json.loads(f.read())
        return [Tweet(**tweet) for tweet in tweets]


### Get a tweet
@app.get(
    path="/tweets/{tweet_id}",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Get a tweet",
    tags=["Tweets"],
)
def get_tweet(tweet_id: UUID = Path(...)):
    """
    Get a tweet

    This endpoint allows you to get a tweet.

    Parameters:
    - Path parameters:
        - tweet_id: UUID

    Returns:
    - Tweet: The tweet with the following fields:
        - tweet_id: UUID
        - user_id: UUID
        - content: str
        - created_at: datetime
        - updated_at: Optional[datetime]
    """
    with open(file="tweets.json", mode="r", encoding="utf-8") as f:
        tweets = json.loads(f.read())
        for tweet_dict in tweets:
            if tweet_dict["tweet_id"] == str(tweet_id):
                tweet_dict["tweet_id"] = str(tweet_id)
                tweet_dict["user_id"] = str(tweet_dict["user_id"])
                tweet_dict["created_at"] = str(tweet_dict["created_at"])
                tweet_dict["updated_at"] = str(tweet_dict["updated_at"])
                return Tweet(**tweet_dict)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tweet not found")

### Create a tweet
@app.post(
    path="/tweets/",
    response_model=Tweet,
    status_code=status.HTTP_201_CREATED,
    summary="Create a tweet",
    tags=["Tweets"],
)
def create_tweet(tweet: Tweet = Body(...)):
    """
    Create tweet

    This endpoint allows you to create a tweet.

    Parameters:
    - Request body:
        - tweet: Tweet

    Returns:
    - Tweet: The newly created tweet with the following fields:
        - tweet_id: UUID
        - user_id: UUID
        - content: str
        - created_at: datetime
        - updated_at: Optional[datetime]
    """
    with open("tweets.json", "r+", encoding="utf-8") as f:
        tweets = json.loads(f.read())
        tweet_dict = tweet.dict()
        tweet_dict["tweet_id"] = str(tweet_dict["tweet_id"])
        tweet_dict["user_id"] = str(tweet_dict["user_id"])
        tweet_dict["created_at"] = str(tweet_dict["created_at"])
        tweet_dict["updated_at"] = str(tweet_dict["updated_at"])
        tweets.append(tweet_dict)
        f.seek(0)
        f.write(json.dumps(tweets, indent=4))
        return tweet

### Update a tweet
@app.put(
    path="/tweets/{tweet_id}",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Update a tweet",
    tags=["Tweets"],
)
def update_tweet(tweet_id: UUID = Path(...), tweet: Tweet = Body(...)):
    """
    Update a tweet

    This endpoint allows you to update a tweet.

    Parameters:
    - Path parameters:
        - tweet_id: UUID
    - Request body:
        - tweet: Tweet

    Returns:
    - Tweet: The updated tweet with the following fields:
        - tweet_id: UUID
        - user_id: UUID
        - content: str
        - created_at: datetime
        - updated_at: Optional[datetime]
    """
    with open("tweets.json", "r+", encoding="utf-8") as f:
        tweets = json.loads(f.read())
        for tweet_dict in tweets:
            if tweet_dict["tweet_id"] == str(tweet_id):
                tweet_dict.update(tweet.dict())
                tweet_dict["tweet_id"] = str(tweet_id)
                tweet_dict["user_id"] = str(tweet_dict["user_id"])
                tweet_dict["created_at"] = str(tweet_dict["created_at"])
                tweet_dict["updated_at"] = str(tweet_dict["updated_at"])
                f.seek(0)
                f.write(json.dumps(tweets, indent=4))
                return Tweet(**tweet_dict)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tweet not found")

### Delete a tweet
@app.delete(
    path="/tweets/{tweet_id}",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Delete a tweet",
    tags=["Tweets"],
)
def delete_tweet(tweet_id: UUID = Path(...)):
    """
    Delete a tweet

    This endpoint allows you to delete a tweet.

    Parameters:
    - Path parameters:
        - tweet_id: UUID

    Returns:
    - Tweet: The deleted tweet with the following fields:
        - tweet_id: UUID
        - user_id: UUID
        - content: str
        - created_at: datetime
        - updated_at: Optional[datetime]
    """
    f = open("tweets.json", "r", encoding="utf-8")
    tweets = json.loads(f.read())
    for tweet_dict in tweets:
        if tweet_dict["tweet_id"] == str(tweet_id):
            tweets.remove(tweet_dict)
            f.close()
            f = open("tweets.json", "w", encoding="utf-8")
            f.write(json.dumps(tweets, indent=4))
            f.close()
            return Tweet(**tweet_dict)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tweet not found")
