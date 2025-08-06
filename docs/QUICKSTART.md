# Quick Start Guide - API Tester

Get up and running with the API Tester application in minutes!

## 🚀 Quick Installation

1. **Install Python 3.8+** (if not already installed)
2. **Install dependencies:**
   ```bash
   python3 -m pip install -r requirements.txt
   ```
3. **Run the application:**
   ```bash
   python3 main.py
   ```

## 🎯 First Steps

### 1. Create Your First Collection
- Click `File > New Collection`
- Name it "My First Collection"

### 2. Add a Test Request
- Right-click your collection → "Add Request"
- Name it "Test API"
- Set method to `GET`
- Enter URL: `https://jsonplaceholder.typicode.com/users/1`
- Click "Send"

### 3. View the Response
- Switch to the "Response" tab
- You should see a 200 status code and JSON response

## 📚 Try the Sample Collection

1. **Import the sample collection:**
   - Click `File > Import Collection`
   - Select `examples/sample_collection.json`
   - Explore the pre-configured requests

2. **Test different HTTP methods:**
   - GET: Retrieve data
   - POST: Create new resources
   - PUT: Update existing resources
   - DELETE: Remove resources

## 🔧 Environment Variables

1. **Create an environment:**
   - Click `Environment > New Environment`
   - Name it "Development"

2. **Add variables:**
   - Select your environment in the sidebar
   - Click "Add Variable"
   - Add: `base_url` = `https://jsonplaceholder.typicode.com`
   - Add: `user_id` = `1`

3. **Use variables in requests:**
   - URL: `{{base_url}}/users/{{user_id}}`
   - Headers: `Authorization: Bearer {{token}}`

## 📝 Pre-request Scripts

Add this to a request's "Pre-request Script" tab:
```javascript
// Set timestamp
pm.environment.set("timestamp", new Date().getTime());

// Generate random ID
pm.environment.set("random_id", Math.random().toString(36).substr(2, 9));
```

## 🧪 Test Scripts

Add this to a request's "Tests" tab:
```javascript
// Test status code
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Test response time
pm.test("Response time is less than 1000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(1000);
});
```

## 🎨 Tips & Tricks

### Keyboard Shortcuts
- `Ctrl/Cmd + S`: Save current request
- `Ctrl/Cmd + Enter`: Send request
- `F5`: Refresh response

### Best Practices
1. **Organize with collections** - Group related APIs together
2. **Use environments** - Separate dev/staging/prod configurations
3. **Write tests** - Automate your API validation
4. **Use variables** - Make requests dynamic and reusable

### Common Use Cases
- **API Documentation Testing** - Verify endpoints work as documented
- **Integration Testing** - Test API integrations
- **Performance Testing** - Monitor response times
- **Regression Testing** - Ensure APIs haven't broken

## 🆘 Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Look at the sample collection in `examples/` for inspiration
- Review the troubleshooting section in the main README

## 🎉 You're Ready!

You now have a powerful API testing tool at your fingertips. Start exploring APIs, building collections, and automating your testing workflow! 