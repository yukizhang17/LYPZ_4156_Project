# 4156_Project (LYPZ)
Class Project for COMS 4156 Advanced Software Engineering Fall 2021.

## Usage:
### Installation:
1. Clone the repo
   ```
   git clone https://github.com/yukizhang17/LYPZ_4156_Project.git
   ```
2. Setup environment 

    In the root directory, choose the following two options.

* Option 1
  ```
  source venv/bin/activate
  ```
* Option 2
  ```
  pip3 install -r requirements.txt
  ``` 
3. Start the API service
    ```
    python3 app.py
    ```

### Endpoints:
## 

### 1. Generate api_key
   
   **HTTP Request:**
   
   ```
   GET http://localhost:5000/generate-apikey
     
   Content-Type: application/x-www-form-urlencoded

   Input: email=YOUR_EMAIL&password=YOUR_PASSWORD
    
   Restriction:
      > You have to verify your email to get your API_KEY
   ```
   
   **Response Sample:**
   ```
    HTTP/1.1 200 OK
    Content-Type: application/json
    {
      "api_key": "eyJ...MoQ",
      "status_code": 200
    }
   ```
   
   ## 
   
   **HTTP Request:**
   
   ```
   POST http://localhost:5000/generate-apikey
     
   Content-Type: application/x-www-form-urlencoded

   Input: email=YOUR_EMAIL&password=YOUR_PASSWORD
    
   Restriction:
      > YOUR_PASSWORD should be at least 8 characters. 
      > You have to verify your email to get your API_KEY
   ```
   
   **Response Sample:**
   ```
    HTTP/1.1 200 OK
    Content-Type: application/json
    {
      "message": "token created, please verified your email before receiving the token",
      "status_code": 200
    }
   ```
   
   ## 
   
### 2. User sign-up
   
   **HTTP Request:**
   
   ```
   POST http://localhost:5000/signup
     
   Content-Type: application/x-www-form-urlencoded

   Input: email=YOUR_EMAIL&password=YOUR_PASSWORD&api_key=YOUR_API_KEY
    
   Restriction:
      > YOUR_EMAIL should be in valid format.
      > YOUR_PASSWORD should be at least 8 characters. 
   ```
   
   **Response Sample:**
   ```
    HTTP/1.1 200 OK
    Content-Type: application/json
    {
      "_id": "6190...83",
      "email": YOUR_EMAIL,
      "email_verified": false
    }
   ```
     
  ## 
   
### 3. User log-in
   
   **HTTP Request:**
   
   ```
   GET http://localhost:5000/login
     
   Content-Type: application/x-www-form-urlencoded

   Input: email=YOUR_EMAIL&password=YOUR_PASSWORD&api_key=YOUR_API_KEY
   ```
   
   **Response Sample:**
   ```
    HTTP/1.1 200 OK
    Content-Type: application/json
    { 
      "access_token": "eyJhb...TnJMA", 
      "scope": "...", 
      "token_type": "Bearer" 
    }
   ```
   
   ## 
   
### 4. Get User Info
   
   **HTTP Request:**
   
   ```
   GET http://localhost:5000/userinfo
     
   Content-Type: application/x-www-form-urlencoded

   Input: token=YOUR_ACCESS_TOKEN
   ```
   
   **Response Sample:**
   ```
    HTTP/1.1 200 OK
    Content-Type: application/json
    {
      "email": YOUR_EMAIL,
      "email_verified": false,
      "name": YOUR_NAME,
      "nickname": YOUR_NICKNAME,
      "picture": YOUR_PICTURE_URL,
      "sub": "auth0|619...9c",
      "updated_at": YOUR_LOG_IN_TIME
    }
   ```
  
  ### 5. Subscribe with keyword
   
   **HTTP Request:**
   
   ```
   POST http://localhost:5000/subscribe
     
   Content-Type: application/x-www-form-urlencoded

   Input: access_token=YOUR_TOKEN&product=YOUR_KEYWORD&type=keyword
   ```
   
   **Response Sample:**
   ```
    HTTP/1.1 200 OK
    Content-Type: application/json
    {
      "reason": "Subscribed successfully!",
      "status_code": 200
    }
     
    Restriction:
      > Fields access_token, product, type are required.
   ```
   
   ## 

   ### 6. Subscribe with productID
   
   **HTTP Request:**
   
   ```
   POST http://localhost:5000/subscribe
     
   Content-Type: application/x-www-form-urlencoded

   Input: access_token=YOUR_TOKEN&product=YOUR_PRODUCTID&type=productID&platform=YOUR_PLATFORM&expected_price=YOUR_PRICE
   ```
   
   **Response Sample:**
   ```
    HTTP/1.1 200 OK
    Content-Type: application/json
    {
      "reason": "Subscribed successfully!",
      "status_code": 200
    }
    Restriction:
      > Fields access_token, product, type, platform are required.
      > YOUR_PLATFORM must be either Amazon or BestBuy.
      > Field expected_price is optional.
   ```
   
   ## 

   ### 7. Subscribe with keyword
   
   **HTTP Request:**
   
   ```
   POST http://localhost:5000/unsubscribe
     
   Content-Type: application/x-www-form-urlencoded

   Input: access_token=YOUR_TOKEN&product=YOUR_PRODUCTID&type=productID
   ```
   
   **Response Sample:**
   ```
    HTTP/1.1 200 OK
    Content-Type: application/json
    {
      "reason": "Unsubscribe successfully!",
      "status_code": 200
    }
    Restriction:
      > Fields access_token, product, type are required.
   ```
   
   ## 

   ### 8. Subscribe with productID
   
   **HTTP Request:**
   
   ```
   POST http://localhost:5000/unsubscribe
     
   Content-Type: application/x-www-form-urlencoded

   Input: access_token=YOUR_TOKEN&product=YOUR_PRODUCTID&type=productID&platform=YOUR_PLATFORM
   ```
   
   **Response Sample:**
   ```
    HTTP/1.1 200 OK
    Content-Type: application/json
    {
      "reason": "Unsubscribe successfully!",
      "status_code": 200
    }
    Restriction:
      > Fields access_token, product, type, platform are required.
      > YOUR_PLATFORM must be either Amazon or BestBuy.
   ```

 
   
   
   


  
     
     
