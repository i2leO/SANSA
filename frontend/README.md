# SANSA Frontend

React + Vite + TypeScript frontend for the SANSA research system.

## Features

- ✅ React 18 with TypeScript
- ✅ Vite for fast development
- ✅ React Router for navigation
- ✅ React Hook Form + Zod validation
- ✅ Tailwind CSS for styling
- ✅ Zustand for state management
- ✅ Axios for API calls
- ✅ Large text mode for accessibility
- ✅ Responsive design

## Prerequisites

- Node.js 18+ and npm

## Installation

```bash
cd frontend
npm install
```

## Configuration

Create `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

## Running the Application

### Development Mode

```bash
npm run dev
```

The application will be available at http://localhost:5173

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── pages/          # Page components
│   │   ├── HomePage.tsx
│   │   ├── RespondentStartPage.tsx
│   │   ├── GeneralInfoPage.tsx
│   │   ├── SANSAFormPage.tsx
│   │   ├── ResultPage.tsx
│   │   ├── SatisfactionPage.tsx
│   │   ├── FoodDiaryPage.tsx
│   │   ├── KnowledgePage.tsx
│   │   ├── FacilitiesPage.tsx
│   │   ├── AdminLoginPage.tsx
│   │   └── AdminDashboard.tsx
│   ├── stores/         # Zustand state stores
│   │   ├── authStore.ts
│   │   └── uiStore.ts
│   ├── lib/            # Utilities
│   │   └── api.ts      # Axios client
│   ├── types/          # TypeScript types
│   │   └── index.ts
│   ├── App.tsx         # Main app component
│   ├── main.tsx        # Entry point
│   └── index.css       # Global styles
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Routes

### Public Routes
- `/` - Home page
- `/start` - Respondent start (enter or create code)
- `/general-info/:code` - General information form
- `/sansa/:code` - SANSA assessment form
- `/result/:visitId` - Assessment results
- `/satisfaction/:visitId` - Satisfaction survey
- `/food-diary/:code` - Food diary
- `/knowledge` - Knowledge center
- `/facilities` - Health facilities

### Protected Routes (Admin/Staff)
- `/admin/login` - Admin login
- `/admin/*` - Admin dashboard

## Features

### Respondent Flow
1. Start assessment (new or existing code)
2. Fill general information
3. Complete SANSA assessment
4. View results and recommendations
5. Complete satisfaction survey
6. Access food diary (optional)

### Admin Features
- User management
- Data export (SPSS CSV)
- Knowledge content management
- Facility management
- Scoring rule configuration

### Accessibility
- Large text mode toggle
- High contrast support
- Keyboard navigation
- Screen reader friendly

## State Management

### Auth Store
```typescript
useAuthStore()
- user: User | null
- isAuthenticated: boolean
- login(user, token)
- logout()
```

### UI Store
```typescript
useUIStore()
- largeTextMode: boolean
- toggleLargeText()
```

## API Integration

The frontend communicates with the FastAPI backend through axios:

```typescript
import apiClient from '@/lib/api'

// Example: Create respondent
const response = await apiClient.post('/respondents', data)

// Authenticated requests automatically include JWT token
```

## Styling

Tailwind CSS is used for styling with custom theme colors:

- **Primary colors**: Blue shades (50-900)
- **Custom font sizes**: `large` (1.125rem), `xlarge` (1.25rem)

## Development Tips

### Adding New Pages
1. Create component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add navigation links as needed

### API Calls
Always use the `apiClient` from `@/lib/api` for automatic token handling.

### Form Validation
Use React Hook Form with Zod schemas for type-safe validation.

### State Management
Use Zustand stores for global state. Keep component state local when possible.

## Build Notes

The build process:
1. TypeScript compilation
2. Vite bundling
3. Output to `dist/` directory

## Environment Variables

- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)

All Vite env vars must be prefixed with `VITE_`.

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Deployment

1. Build the application:
```bash
npm run build
```

2. Serve the `dist/` directory with a web server:
```bash
npm run preview  # For testing
```

3. For production, use nginx, Apache, or similar to serve static files.

## Known Limitations

- Some pages (SANSA form details, food diary entry form) are placeholder implementations
- Full form validation for all assessment items needs implementation
- Photo upload for food diary needs implementation
- Admin dashboard functionality needs full implementation

## Next Steps for Full Implementation

1. **Complete SANSA Form**: Implement all 4 screening + 12 dietary questions with proper scoring
2. **MNA Form**: Add full MNA assessment form
3. **BIA Form**: Add body composition measurement form
4. **Food Diary**: Implement photo upload and diary management
5. **Admin Features**: Complete all CRUD operations for admin panel
6. **Export**: Add date filters and format options
7. **Knowledge Posts**: Add rich text editor for content
8. **Facilities**: Add map integration
9. **Testing**: Add unit and integration tests
10. **Documentation**: Add inline code documentation

## Support

For issues or questions, refer to the main project documentation.
