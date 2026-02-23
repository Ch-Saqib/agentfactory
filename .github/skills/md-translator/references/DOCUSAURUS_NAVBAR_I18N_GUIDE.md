# Docusaurus Navbar & Translation Button - In-Depth Official Format Guide

**Date Generated**: February 22, 2026  
**Docusaurus Version**: v3.9+ (Current in Agent Factory)  
**Documentation Source**: https://docusaurus.io/docs/api/docusaurus-config and official themes

---

## 📋 TABLE OF CONTENTS

1. [Quick Overview](#quick-overview)
2. [Current Agent Factory Setup Analysis](#current-agent-factory-setup-analysis)
3. [Official Navbar Items Type Reference](#official-navbar-items-type-reference)
4. [Translation Button (Locale Dropdown) Setup](#translation-button-locale-dropdown-setup)
5. [Official i18n Configuration](#official-i18n-configuration)
6. [Step-by-Step Implementation](#step-by-step-implementation)
7. [Advanced Configuration Examples](#advanced-configuration-examples)

---

## QUICK OVERVIEW

### What is the Navbar in Docusaurus?

The navbar is configured in **`docusaurus.config.ts`** under `themeConfig.navbar`. It controls:
- Navbar title & logo
- Navigation items (links, dropdowns, docs, etc.)
- Position of items (left/right)
- Search bar placement
- **Locale dropdown (translation button)** ← Most relevant for i18n

### What is the Translation Button?

The **locale dropdown** is a special navbar item (`type: 'localeDropdown'`) that:
- Displays all available locales (languages)
- Allows users to switch languages while staying on the same page
- Requires `i18n` configuration to be set up first
- Automatically uses locale labels from `i18n.localeConfigs`

---

## CURRENT AGENT FACTORY SETUP ANALYSIS

### Current Configuration (from `docusaurus.config.ts`)

```typescript
// CURRENT STATE
i18n: {
  defaultLocale: "en",
  locales: ["en"],  // ← ONLY English, no multi-language
},

// CURRENT NAVBAR
navbar: {
  title: "Agent Factory",
  hideOnScroll: false,
  items: [
    {
      to: "/factory",
      position: "left",
      label: "🏭 Factory",
      className: "navbar-factory-link",
    },
    {
      type: "docSidebar",
      sidebarId: "tutorialSidebar",
      position: "left",
      label: "Book",
    },
    {
      to: "/progress",
      position: "left",
      label: "Progress",
    },
    {
      to: "/leaderboard",
      position: "left",
      label: "Leaderboard",
    },
    {
      type: "custom-searchBar",  // ← Custom search component
      position: "right",
    },
    {
      type: "custom-navbarAuth",  // ← Custom auth component
      position: "right",
    },
  ],
},
```

### Current Status: ✅ **No Translation Button Needed Yet**

**Why?** Because:
- Only one locale is configured (`locales: ["en"]`)
- Translation button only appears when `locales.length > 1`
- Custom navbar items are being used (good for Agent Factory's auth flow)

---

## OFFICIAL NAVBAR ITEMS TYPE REFERENCE

Docusaurus provides these **official navbar item types**:

### 1. **Link** (Default)
Regular internal or external link.

```typescript
{
  type: "default",  // Optional (default = link)
  to: "docs/introduction",  // Internal route
  // OR
  href: "https://example.com",  // External URL
  label: "Documentation",
  position: "left" | "right",  // Default: "left"
  activeBasePath: "docs",  // Mark as active
  activeBaseRegex: "docs/(next|v8)",  // More flexible
  className: "custom-class",
  target: "_blank",
}
```

### 2. **Dropdown**
Multi-level menu with nested items.

```typescript
{
  type: "dropdown",
  label: "Community",
  position: "left",
  items: [
    {
      label: "Facebook",
      href: "https://facebook.com",
    },
    {
      type: "doc",
      label: "Social",
      docId: "social",
    },
    // Only link-like items allowed in dropdowns
  ],
}
```

### 3. **Doc Link**
Link directly to a specific doc.

```typescript
{
  type: "doc",
  docId: "introduction",  // Must exist
  label: "Docs",
  position: "left",
  docsPluginId: "default",  // Which docs plugin
}
```

### 4. **Doc Sidebar**
Link to first doc in a sidebar (best for dynamic sidebars).

```typescript
{
  type: "docSidebar",
  sidebarId: "api",  // Must exist in sidebars.js
  label: "API",
  position: "left",
  docsPluginId: "default",
}
```

### 5. **Docs Version Dropdown**
Switch between Docusaurus versions.

```typescript
{
  type: "docsVersionDropdown",
  position: "right",
  dropdownItemsBefore: [
    // Items before version list
  ],
  dropdownItemsAfter: [
    {
      to: "/versions",
      label: "All versions",
    },
  ],
  dropdownActiveClassDisabled: false,
}
```

### 6. **⭐ LOCALE DROPDOWN** (Translation Button)
**This is what you need for translations!**

```typescript
{
  type: "localeDropdown",
  position: "left" | "right",  // Usually right
  dropdownItemsBefore: [],
  dropdownItemsAfter: [
    {
      to: "https://example.com/help-translate",
      label: "Help us translate",
    },
  ],
  queryString: "?persistLocale=true",  // Optional: append to URL
}
```

### 7. **Search Bar**
Built-in search functionality.

```typescript
{
  type: "search",
  position: "right",
  className: "search-bar",
}
```

### 8. **Custom HTML**
Raw HTML in navbar.

```typescript
{
  type: "html",
  position: "right",
  value: '<button>Give feedback</button>',
  className: "navbar-html-item",
}
```

---

## TRANSLATION BUTTON (LOCALE DROPDOWN) SETUP

### Official Format from Docusaurus Docs

```typescript
// Step 1: Enable i18n in Site Config
export default {
  i18n: {
    defaultLocale: "en",
    locales: ["en", "fr", "fa"],  // Add your locales here
    path: "i18n",  // Where translation files live
    localeConfigs: {
      en: {
        label: "English",  // Displayed in dropdown
        direction: "ltr",
        htmlLang: "en-US",
        calendar: "gregory",
        path: "en",
        translate: false,  // Already in English
        url: "https://docusaurus.io",  // Optional
      },
      fr: {
        label: "Français",  // Displayed in dropdown
        direction: "ltr",
        htmlLang: "fr-FR",
        path: "fr",
        translate: true,  // Needs translation
      },
      fa: {
        label: "فارسی",  // Displayed in dropdown (RTL)
        direction: "rtl",  // Right-to-left
        htmlLang: "fa-IR",
        path: "fa",
        translate: true,
      },
    },
  },
};
```

### Step 2: Add Locale Dropdown to Navbar

```typescript
export default {
  themeConfig: {
    navbar: {
      items: [
        // ... existing items ...
        {
          type: "localeDropdown",
          position: "right",  // Usually on right side
          dropdownItemsAfter: [
            {
              to: "https://github.com/facebook/docusaurus/discussions/3317",
              label: "Help us translate",
            },
          ],
        },
        // or for query string persistence:
        {
          type: "localeDropdown",
          position: "right",
          queryString: "?persistLocale=true",  // Append to URL on switch
        },
      ],
    },
  },
};
```

### Translation File Structure

After setting up i18n, Docusaurus expects this folder structure:

```
project-root/
├── docusaurus.config.ts
├── docs/
│   ├── intro.md
│   └── ...
└── i18n/
    ├── en/  (optional, only for non-default locales sometimes)
    │   ├── docusaurus-theme-classic/
    │   │   ├── navbar.json
    │   │   └── footer.json
    │   ├── docusaurus-plugin-content-docs/
    │   │   └── current/
    │   │       ├── intro.md
    │   │       └── ...
    │   └── code.json
    ├── fr/
    │   ├── docusaurus-theme-classic/
    │   │   ├── navbar.json
    │   │   └── footer.json
    │   ├── docusaurus-plugin-content-docs/
    │   │   └── current/
    │   │       ├── intro.md
    │   │       └── ...
    │   └── code.json
    └── fa/
        ├── docusaurus-theme-classic/
        │   ├── navbar.json
        │   └── footer.json
        ├── docusaurus-plugin-content-docs/
        │   └── current/
        │       └── ...
        └── code.json
```

---

## OFFICIAL I18N CONFIGURATION

### Complete i18n Object Specification

```typescript
i18n: {
  // REQUIRED: Default locale (doesn't appear in URL)
  defaultLocale: "en",
  
  // REQUIRED: All locales your site supports
  locales: ["en", "fr", "de", "es", "ja", "zh-CN"],
  
  // OPTIONAL: Where translation files are stored
  // Defaults to "i18n" folder
  path: "i18n",
  
  // Per-locale configuration
  localeConfigs: {
    en: {
      // Label shown in locale dropdown
      label: "English",
      
      // Text direction (ltr or rtl)
      direction: "ltr",  // default
      
      // HTML lang attribute
      htmlLang: "en-US",  // default: "en"
      
      // Calendar system for dates
      // Options: "gregory", "persian", "buddhist", etc.
      calendar: "gregory",  // default
      
      // Path for this locale's content
      path: "en",  // defaults to locale name
      
      // Should translation process run for this locale?
      translate: true,  // default: true
      
      // Override site URL for this locale
      // Useful for multi-domain deployment
      url: "https://en.example.com",  // optional
      
      // Override baseUrl for this locale
      baseUrl: "/en/",  // optional
    },
    
    fr: {
      label: "Français",
      direction: "ltr",
      htmlLang: "fr-FR",
      path: "fr",
      translate: true,
    },
    
    fa: {
      label: "فارسی",
      direction: "rtl",  // RIGHT-TO-LEFT language
      htmlLang: "fa-IR",
      path: "fa",
      translate: true,
    },
  },
}
```

### URL Behavior

| Locale | URL | Example |
|--------|-----|---------|
| Default (en) | No prefix | `https://example.com/docs` |
| Non-default (fr) | `/fr/` prefix | `https://example.com/fr/docs` |
| Non-default (fa) | `/fa/` prefix | `https://example.com/fa/docs` |

---

## STEP-BY-STEP IMPLEMENTATION

### Phase 1: Basic Setup (If Adding Translation to Agent Factory)

#### Step 1.1: Update `i18n` Configuration

```typescript
// docusaurus.config.ts
const config: Config = {
  // ... existing config ...

  i18n: {
    defaultLocale: "en",
    // Add languages here when ready
    locales: ["en"],  // Change to ["en", "fr", "es"] when ready
    localeConfigs: {
      en: {
        label: "English",
        direction: "ltr",
        htmlLang: "en-US",
        calendar: "gregory",
        path: "en",
        translate: false,  // Already in English
      },
      // Add more locales here later
      // fr: {
      //   label: "Français",
      //   direction: "ltr",
      //   htmlLang: "fr-FR",
      //   path: "fr",
      //   translate: true,
      // },
    },
  },
};
```

#### Step 1.2: Add Locale Dropdown to Navbar

```typescript
navbar: {
  title: "Agent Factory",
  hideOnScroll: false,
  items: [
    // ... existing items ...
    
    // Add this ONLY when you have multiple locales
    // {
    //   type: "localeDropdown",
    //   position: "right",
    //   dropdownItemsAfter: [
    //     {
    //       to: "https://github.com/panaversity/...",
    //       label: "Help us translate",
    //     },
    //   ],
    // },
    
    {
      type: "custom-searchBar",
      position: "right",
    },
    {
      type: "custom-navbarAuth",
      position: "right",
    },
  ],
},
```

### Phase 2: When Adding Second Language

#### Step 2.1: Update i18n Config

```typescript
i18n: {
  defaultLocale: "en",
  locales: ["en", "fr"],  // Add French
  localeConfigs: {
    en: {
      label: "English",
      direction: "ltr",
      htmlLang: "en-US",
      path: "en",
      translate: false,
    },
    fr: {
      label: "Français",
      direction: "ltr",
      htmlLang: "fr-FR",
      path: "fr",
      translate: true,
    },
  },
},
```

#### Step 2.2: Enable Locale Dropdown in Navbar

```typescript
items: [
  // ... existing items ...
  {
    type: "localeDropdown",
    position: "right",  // Before auth/search
    dropdownItemsAfter: [
      {
        to: "https://github.com/panaversity/...",
        label: "Help us translate",
      },
    ],
  },
  {
    type: "custom-searchBar",
    position: "right",
  },
  {
    type: "custom-navbarAuth",
    position: "right",
  },
],
```

#### Step 2.3: Extract Translation Keys

```bash
# Run this command to create JSON files for translation
npm run write-translations -- --locale fr
```

This generates:
- `i18n/fr/code.json` - React component text
- `i18n/fr/docusaurus-theme-classic/navbar.json` - Navbar translations
- `i18n/fr/docusaurus-plugin-content-docs/current/` - Docs content

#### Step 2.4: Translate Files

Manually or via platform (Crowdin, Weblate, etc.) fill in translated values:

```json
// i18n/fr/docusaurus-theme-classic/navbar.json
{
  "item.label.Factory": {
    "message": "Usine",
    "description": "Navbar item label"
  },
  "item.label.Book": {
    "message": "Livre",
    "description": "Sidebar label"
  },
  "item.label.Progress": {
    "message": "Progression",
    "description": "Progress navbar item"
  }
}
```

#### Step 2.5: Test

```bash
# Start development server for French locale
npm run start -- --locale fr

# Build all locales
npm run build
# Creates: build/index.html, build/fr/index.html
```

---

## ADVANCED CONFIGURATION EXAMPLES

### Example 1: Multi-Domain Deployment with Locale URLs

For deploying each locale to a different domain:

```typescript
i18n: {
  defaultLocale: "en",
  locales: ["en", "fr", "es"],
  localeConfigs: {
    en: {
      label: "English",
      htmlLang: "en-US",
      url: "https://en.docusaurus.io",  // Subdomain
      baseUrl: "/",
    },
    fr: {
      label: "Français",
      htmlLang: "fr-FR",
      url: "https://fr.docusaurus.io",  // Different domain
      baseUrl: "/",
    },
    es: {
      label: "Español",
      htmlLang: "es-ES",
      url: "https://es.docusaurus.io",  // Different domain
      baseUrl: "/",
    },
  },
},

// Navbar will redirect to appropriate domain when switching
```

### Example 2: Right-to-Left Language with Dropdown

```typescript
i18n: {
  defaultLocale: "en",
  locales: ["en", "ar", "he"],  // Arabic, Hebrew
  localeConfigs: {
    en: {
      label: "English",
      direction: "ltr",
      htmlLang: "en-US",
    },
    ar: {
      label: "العربية",  // Arabic label
      direction: "rtl",  // ← Right-to-left!
      htmlLang: "ar",
      calendar: "islamic",  // Islamic calendar
    },
    he: {
      label: "עברית",  // Hebrew label
      direction: "rtl",
      htmlLang: "he-IL",
    },
  },
},

navbar: {
  items: [
    {
      type: "localeDropdown",
      position: "right",
      // In RTL locale, this will flip to "left" automatically
    },
  ],
},
```

### Example 3: Query String Persistence (Server-Side Locale Detection)

```typescript
navbar: {
  items: [
    {
      type: "localeDropdown",
      position: "right",
      // Append query string when locale changes
      // Server can detect and set cookie for persistence
      queryString: "?persistLocale=true",
    },
  ],
},
```

### Example 4: Complex Navbar with All Items Types

```typescript
navbar: {
  title: "Agent Factory",
  logo: {
    alt: "Logo",
    src: "img/logo.svg",
    srcDark: "img/logo_dark.svg",
  },
  hideOnScroll: false,
  style: "primary",
  items: [
    // Left side
    {
      type: "docSidebar",
      sidebarId: "book",
      label: "📚 Book",
      position: "left",
    },
    {
      type: "dropdown",
      label: "Learning Paths",
      position: "left",
      items: [
        {
          type: "doc",
          docId: "foundations",
          label: "Foundations",
        },
        {
          type: "doc",
          docId: "advanced",
          label: "Advanced",
        },
        {
          type: "html",
          value: '<hr>',
        },
        {
          label: "External Docs",
          href: "https://example.com",
        },
      ],
    },
    {
      type: "search",
      position: "right",  // Move search here
    },
    // Right side
    {
      type: "localeDropdown",
      position: "right",
    },
    {
      type: "custom-navbarAuth",
      position: "right",
    },
  ],
},
```

---

## KEY TAKEAWAYS FOR AGENT FACTORY

### ✅ **What's Working**

- Custom navbar components (`custom-searchBar`, `custom-navbarAuth`)
- Single-language setup is clean and simple
- Navbar structure follows Docusaurus conventions

### 🔄 **When You Add Translations**

1. **Enable multi-locale:** Change `locales: ["en"]` → `locales: ["en", "fr"]`
2. **Add locale configs:** Define label, direction, language for each locale
3. **Add locale dropdown:** Add `type: "localeDropdown"` to navbar items
4. **Create translation files:** Run `write-translations`, populate i18n/ folder
5. **Deploy single or multi-domain:** Depends on your hosting strategy

### 📝 **Translation Files Needed**

```
i18n/
├── fr/
│   ├── docusaurus-theme-classic/
│   │   ├── navbar.json        ← Button labels
│   │   └── footer.json        ← Footer labels
│   ├── docusaurus-plugin-content-docs/current/
│   │   └── *.md              ← Translated docs
│   └── code.json             ← React text labels
```

### 🚀 **Official Docusaurus Resources**

- Navbar Config: https://docusaurus.io/docs/api/themes/configuration#navbar
- i18n Overview: https://docusaurus.io/docs/i18n/introduction
- i18n Tutorial: https://docusaurus.io/docs/i18n/tutorial
- Theme Config: https://docusaurus.io/docs/api/docusaurus-config#i18n

---

**End of Guide**

Generated: February 22, 2026
For: Panaversity Agent Factory
Docusaurus: v3.9.2
