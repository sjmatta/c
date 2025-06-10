# Component Library Reference

This document defines the available libraries and components for AI generation.

## 📦 Available Libraries

### Core React:
- `react` - React library
- `react-dom` - React DOM
- `lodash` - Utility library (available as global `_`)

### UI Enhancement:
- `@heroicons/react/24/outline` - Beautiful outline icons
- `@heroicons/react/24/solid` - Beautiful solid icons  
- `framer-motion` - Smooth animations and transitions

### CSS Framework:
- **Tailwind CSS** - Complete utility-first CSS framework

## 🎨 Quick Examples

### Using Heroicons:
```jsx
import { UserIcon, ChevronDownIcon, HeartIcon } from '@heroicons/react/24/outline'

<UserIcon className="w-5 h-5 text-blue-600" />
```

### Using Framer Motion:
```jsx
import { motion } from 'framer-motion'

<motion.button 
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  className="bg-blue-600 text-white px-4 py-2 rounded"
>
  Click me!
</motion.button>
```

## Available Components

### Pagination Component
Location: `components/Pagination.tsx`

**Usage:**
```jsx
import { Pagination } from './components/Pagination';

<Pagination 
  currentPage={currentPage}
  totalPages={totalPages}
  onPageChange={handlePageChange}
/>
```

**Props:**
- `currentPage: number` - Current active page (1-indexed)
- `totalPages: number` - Total number of pages
- `onPageChange: (page: number) => void` - Callback when page changes

**Features:**
- Fully styled with Tailwind CSS
- Accessible with ARIA attributes
- Proper disabled states
- Focus management for keyboard navigation

### Button Component (Inline)
For standalone buttons, use these Tailwind class patterns:

**Primary Button:**
```jsx
className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
```

**Secondary Button:**
```jsx
className="border border-gray-300 bg-white hover:bg-gray-100 text-gray-900 font-medium py-2 px-4 rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
```

## Design System Patterns

### Tables
- Container: `overflow-x-auto`
- Table: `min-w-full bg-white border border-gray-200`
- Headers: `bg-gray-100 px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase`
- Cells: `px-6 py-4 whitespace-nowrap`

### Cards  
- Container: `bg-white rounded-lg shadow-lg p-6`
- Header: `text-lg font-semibold text-gray-900 mb-4`

### Form Elements
- Input: `border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500`
- Label: `block text-sm font-medium text-gray-700 mb-2`