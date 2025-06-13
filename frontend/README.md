# ResourceWise Frontend

A modern React application built with Vite, TypeScript, and Material-UI for intelligent resource allocation management.

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI) v6
- **Styling**: Material-UI Theme System
- **Icons**: Material-UI Icons
- **Development**: Hot Module Replacement (HMR)

## Prerequisites

- Node.js (v18 or higher)
- npm or yarn package manager

## Installation

1. **Install dependencies**:

   ```bash
   npm install
   ```

2. **Start the development server**:

   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:5173` (or the next available port).

## Available Scripts

- `npm run dev` - Start development server with HMR
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Run ESLint with auto-fix
- `npm run format` - Format code with Prettier
- `npm run format:check` - Check if code is formatted with Prettier

## Project Structure

```
src/
├── components/           # React components
│   ├── common/          # Reusable common components
│   │   ├── CustomButton.tsx
│   │   └── CustomCard.tsx
│   ├── Header.tsx       # Navigation header
│   ├── Hero.tsx         # Hero section
│   ├── Features.tsx     # Features showcase
│   ├── About.tsx        # About section
│   └── Footer.tsx       # Footer component
├── theme/               # Material-UI theme configuration
│   └── theme.ts
├── App.tsx              # Main app component
├── main.tsx            # Application entry point
└── index.css           # Global styles
```

## Features

- **Responsive Design**: Mobile-first approach with Material-UI breakpoints
- **Theme System**: Custom blue/navy theme matching brand colors
- **Reusable Components**: Common components for consistent UI
- **TypeScript**: Full type safety throughout the application
- **Hot Reloading**: Instant updates during development

## Material-UI Configuration

The application uses a custom Material-UI theme with:

- **Primary Color**: Blue (#2563eb)
- **Secondary Color**: Navy (#1e1b4b)
- **Typography**: Roboto font family
- **Responsive Breakpoints**: Mobile, tablet, desktop

## Development Guidelines

- Use Material-UI components instead of custom CSS when possible
- Follow TypeScript best practices with proper type annotations
- Maintain consistent component structure and naming conventions
- Use the custom theme for colors and spacing
- Format code with Prettier before committing: `npm run format`
- Ensure code passes linting: `npm run lint`

## Build and Deployment

1. **Build for production**:

   ```bash
   npm run build
   ```

2. **Preview production build**:
   ```bash
   npm run preview
   ```

The built files will be in the `dist/` directory, ready for deployment to any static hosting service.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Follow the existing code style and component patterns
2. Format code before committing: `npm run format`
3. Run linting before committing: `npm run lint`
4. Test changes in development mode before building
5. Ensure responsive design works on all breakpoints
