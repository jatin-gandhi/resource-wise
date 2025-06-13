import { createTheme } from '@mui/material/styles';

// Color palette
export const color_navy_blue = '#26266D';
const color_deep_blue = '#130739';
const color_very_light_grey = '#EFF0F1';
const color_grey = '#E5E5E5';
const color_ocure_yellow = '#FFF0C5';
const color_white = '#ffffff';
const color_green = '#009F84';
const color_dark_yellow = '#FFD86E';
const color_deep_red = '#D0182B';
const color_bright_blue = '#006EFF';
const color_grey_80 = '#5D5D5D';

export const theme = createTheme({
  palette: {
    primary: {
      main: color_navy_blue,
      contrastText: color_white,
      dark: color_deep_blue,
      light: color_bright_blue,
    },
    secondary: {
      main: color_grey,
      light: color_very_light_grey,
      dark: color_grey_80,
    },
    info: {
      main: color_ocure_yellow,
    },
    success: {
      main: color_green,
    },
    warning: {
      main: color_dark_yellow,
    },
    error: {
      main: color_deep_red,
    },
    background: {
      default: color_white,
      paper: color_white,
    },
    text: {
      primary: color_deep_blue,
      secondary: color_grey_80,
    },
  },
  typography: {
    fontFamily: "'Lato', sans-serif",
    fontSize: 14,
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      color: color_deep_blue,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      color: color_deep_blue,
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 600,
      color: color_deep_blue,
    },
    h4: {
      fontSize: '1.25rem',
      fontWeight: 500,
      color: color_deep_blue,
    },
    h5: {
      fontSize: '1.125rem',
      fontWeight: 500,
      color: color_deep_blue,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
      color: color_deep_blue,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
          padding: '10px 24px',
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(38, 38, 109, 0.3)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 12px rgba(0, 0, 0, 0.08)',
          border: `1px solid ${color_very_light_grey}`,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: color_navy_blue,
            },
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
          backgroundColor: color_white,
          color: color_deep_blue,
        },
      },
    },
  },
});

// Custom navy color palette
export const navyPalette = {
  50: '#f0f4ff',
  100: '#e0e8ff',
  200: '#c7d2fe',
  300: '#a5b4fc',
  400: '#818cf8',
  500: '#6366f1',
  600: '#4f46e5',
  700: '#4338ca',
  800: '#3730a3',
  900: '#312e81',
  950: '#1e1b4b',
};
