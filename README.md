# 4156_Project (LYPZ)
Class Project for COMS 4156 Advanced Software Engineering Fall 2021.

## Usage:
### Option 1: Heroku
   ```
   https://whispering-peak-99211.herokuapp.com/
   ```

### Option 2: Local
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
3. Add phantomjs executable path to PATH or in file \application_services\price_fetching_services.py replace the webdriver initialization step with the following:

    ```
    PANTHOMJS_PATH = 'your//path//to//phantomjs.exe'
    driver = webdriver.PhantomJS(PANTHOMJS_PATH)
    ```
4. Start the API service
    ```
    python3 app.py
    ```

### Endpoints:
## 

### 1. Generate api_key
   
   **HTTP Request:**
   
   ```
   GET https://whispering-peak-99211.herokuapp.com/generate-apikey
     
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
   POST https://whispering-peak-99211.herokuapp.com/generate-apikey
     
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
   POST https://whispering-peak-99211.herokuapp.com/signup
     
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
   GET https://whispering-peak-99211.herokuapp.com/login
     
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
   GET https://whispering-peak-99211.herokuapp.com/userinfo
     
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
   POST https://whispering-peak-99211.herokuapp.com/subscribe
     
   Content-Type: application/x-www-form-urlencoded

   Input: access_token=YOUR_TOKEN&product=YOUR_KEYWORD&type=keyword

  Restriction:
      > Fields access_token, product, type are required.

   ```
   
   **Response Sample:**
   ```
    HTTP/1.1 200 OK
    Content-Type: application/json
    {
      "reason": "Subscribed successfully!",
      "status_code": 200
    }
     
   ```
   
   ## 

   ### 6. Subscribe with productID
   
   **HTTP Request:**
   
   ```
   POST https://whispering-peak-99211.herokuapp.com/subscribe
     
   Content-Type: application/x-www-form-urlencoded

   Input: access_token=YOUR_TOKEN&product=YOUR_PRODUCTID&type=productID&platform=YOUR_PLATFORM&expected_price=YOUR_PRICE
  
  Restriction:
      > Fields access_token, product, type, platform are required.
      > YOUR_PLATFORM must be either Amazon or BestBuy.
      > Field expected_price is optional.

   ```
   
   **Response Sample:**
   ```
    HTTP/1.1 200 OK
    Content-Type: application/json
    {
      "reason": "Subscribed successfully!",
      "status_code": 200
    }
    
   ```
   
   ## 

   ### 7. Unsubscribe with keyword
   
   **HTTP Request:**
   
   ```
   POST https://whispering-peak-99211.herokuapp.com/unsubscribe
     
   Content-Type: application/x-www-form-urlencoded

   Input: access_token=YOUR_TOKEN&product=YOUR_PRODUCTID&type=productID&expected_price=YOUR_PRICE
   
  Restriction:
      > Fields access_token, product, type are required.
      > Field expected_price is optional.
   ```
   
   **Response Sample:**
   ```
    HTTP/1.1 200 OK
    Content-Type: application/json
    {
      "reason": "Unsubscribe successfully!",
      "status_code": 200
    }

   ```
   
   ## 

   ### 8. Unsubscribe with product ID
   
   **HTTP Request:**
   
   ```
   POST https://whispering-peak-99211.herokuapp.com/unsubscribe
     
   Content-Type: application/x-www-form-urlencoded

   Input: access_token=YOUR_TOKEN&product=YOUR_PRODUCTID&type=productID&platform=YOUR_PLATFORM

  Restriction:
      > Fields access_token, product, type, platform are required.
      > YOUR_PLATFORM must be either Amazon or BestBuy.
   ```
   
   **Response Sample:**
   ```
    HTTP/1.1 200 OK
    Content-Type: application/json
    {
      "reason": "Unsubscribe successfully!",
      "status_code": 200
    }

   ```

   ## 

   ### 9. Compare prices for a keyword or product ID （Local only）
   
   **HTTP Request:**
   
   ```
   POST http://127.0.0.1:5000/compare

   Content-Type: application/x-www-form-urlencoded

   Input: access_token=YOUR_TOKEN&keyword=KEYWORD&item_id=PRODUCT_ID&platform=PRODUCT_PLATFORM

  Restriction:
      > Fields access_token is required.
      > Field keyword or fields item_id and platform are required.
      > PRODUCT_PLATFORM must be either "amazon" or "bestbuy".
   ```
   
   **Response Sample:**
   ```
    HTTP/1.1 200 OK
    Content-Type: application/json
    {
      "amazon_price": 418.38,
      "bestbuy_price": 195.55,
      "timestamp": "2021-11-15 08:47:09.543926"
    }

   ```
 
### Client:
## 
1. Start the client service
    ```
    cd client
    python3 app.py
    ```
2. Access frontend 
    ```
    visit http://localhost:3000/ in your browser
    ```
