# DJ-AI Frontend

Modern, maintainable frontend for the DJ-AI application.

## Overview

This frontend provides a user interface for searching tracks, managing playlists, and interacting with the DJ-AI backend API. It is built with Node.js and serves static HTML, CSS, and JavaScript files.

## Quick Start

1. Install dependencies:
    ```bash
    npm install
    ```
2. Start the frontend server:
    ```bash
    npm start
    ```
3. Open your browser at [http://localhost:3000](http://localhost:3000)

> Make sure the backend API is running on port 8080 for full functionality.

## Project Structure

```
frontend/
├── public/
│   ├── index.html         # Main landing page
│   ├── app.html           # Main app UI
│   ├── login.html         # Login page
│   ├── playlists.html     # Playlist management
│   ├── profile.html       # User profile
│   ├── css/               # Stylesheets
│   └── js/                # JavaScript modules
│       ├── playlist-ui.js
│       ├── services/
│       └── utils/
├── server.js              # Express server
├── package.json           # Node.js dependencies
└── README.md              # This file
```

## Architecture

- **UI Layer**: Handles DOM manipulation and user interaction (e.g., playlist-ui.js)
- **Services Layer**: Business logic and API communication (e.g., services/playlist-service.js)
- **Utils Layer**: Utility functions and HTTP client (e.g., utils/api-client.js)

See [public/js/README.md](public/js/README.md) for detailed code documentation.

## Development Notes

- The frontend is optimized for modern browsers and mobile devices.
- All API requests are routed to the backend at http://localhost:8080 by default.
- Environment variables can be set in config.js if needed.

## Contributing

Contributions are welcome after April 2026. Please see the main repository guidelines for details.

---

For backend and API documentation, see the main project README.

### Installation
```bash
cd frontend
npm install
```

### Development
```bash
npm start
```
Server runs on http://localhost:3000

## 📂 Project Structure

```
frontend/
├── public/                 # Static files
│   ├── *.html             # HTML pages
│   ├── css/               # Stylesheets
│   └── js/                # JavaScript
│       ├── services/      # Business logic
│       ├── utils/         # Utilities
│       └── *-ui.js        # UI controllers
│
├── config.js              # Server configuration
├── server.js              # Static file server
└── package.json           # Dependencies
```

## 🏗️ Architecture

### Three-Layer Architecture

1. **Utils Layer** - Low-level utilities (HTTP client, helpers)
2. **Services Layer** - Business logic and API communication
3. **UI Layer** - DOM manipulation and event handling

### Data Flow
```
User Action → UI Controller → Service → API Client → Backend
                    ↓              ↓          ↓
                Update DOM    Business Logic  HTTP
```

## 📄 Pages

| Page | URL | Status | Description |
|------|-----|--------|-------------|
| Landing | `/` | ✅ Ready | Homepage |
| Login | `/login` | ⚠️ Legacy | User login |
| Register | `/register` | ⚠️ Legacy | User registration |
| Search | `/app` | ⚠️ Legacy | Track search |
| **Playlists** | **`/playlists`** | **✅ Refactored** | **Playlist management** |
| Profile | `/profile` | ⚠️ Legacy | User profile |

## 🔧 Configuration

### API Configuration
Edit `public/js/config.js`:
```javascript
const AppConfig = {
    api: {
        baseUrl: 'http://localhost:8080',
        prefix: '/api/v1',
        timeout: 30000
    }
};
```

### Server Configuration
Edit `config.js` in root:
```javascript
module.exports = {
    port: 3000,
    staticDir: 'public'
};
```

## 🛠️ Development

### Adding a New Feature

1. **Create Service** (`services/feature-service.js`)
   ```javascript
   class FeatureService {
       constructor() {
           this.apiClient = apiClient;
       }
       
       async getData() {
           return await this.apiClient.get('/endpoint');
       }
   }
   ```

2. **Create UI Controller** (`feature-ui.js`)
   ```javascript
   class FeatureUIController {
       constructor() {
           this.service = featureService;
       }
       
       init() {
           this._attachEventListeners();
       }
   }
   ```

3. **Update HTML**
   ```html
   <script src="js/utils/api-client.js"></script>
   <script src="js/services/feature-service.js"></script>
   <script src="js/feature-ui.js"></script>
   ```

### Code Style

- Use JSDoc comments for all functions
- Follow camelCase for variables/functions
- Use PascalCase for classes
- Prefix private methods with `_`
- Always handle errors gracefully

### Testing

```bash
# Run linter
npm run lint

# Run tests (when implemented)
npm test
```

## 🔐 Security

- HTTP-only cookies for authentication
- XSS protection via HTML escaping
- CSRF protection via SameSite cookies
- Input validation on all forms
- Automatic token refresh

## 🐛 Troubleshooting

### Common Issues

**"apiClient is not defined"**
- Ensure `utils/api-client.js` is loaded before service files

**401 errors not refreshing**
- Check backend refresh token endpoint
- Verify cookies are being sent

**CORS errors**
- Ensure backend CORS is configured
- Check `credentials: 'include'` in fetch calls

## 📈 Performance

- No external JavaScript dependencies (except Tailwind CSS)
- Minimal bundle size
- Lazy loading of features
- Optimized for fast page loads

## 🤝 Contributing

### Refactoring Guidelines

When refactoring a page:

1. Read [MIGRATION.md](public/js/MIGRATION.md)
2. Follow the playlist pattern
3. Create service file
4. Create UI controller
5. Update HTML imports
6. Test thoroughly
7. Update documentation

## 📞 Support

- **Documentation:** See markdown files in this directory
- **Code Examples:** Check refactored playlist feature
- **Questions:** Contact development team

## 📝 License

See main project LICENSE file.

## 🎉 Acknowledgments

- Refactored structure by GitHub Copilot (Jan 2026)
- Based on modern frontend best practices
- Inspired by clean architecture principles

---

**For detailed documentation, start with [QUICK_START.md](QUICK_START.md) or [public/js/README.md](public/js/README.md)**