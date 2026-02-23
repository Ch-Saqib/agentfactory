# Agent Factory - Navbar i18n Implementation Reference

**Current Status**: Single-language (English only)  
**Translation Status**: ❌ Not yet enabled  
**Last Updated**: February 22, 2026

---

## 📊 CURRENT VS. RECOMMENDED

### Current Configuration (English Only)

```typescript
// docusaurus.config.ts - CURRENT
export default {
  i18n: {
    defaultLocale: "en",
    locales: ["en"],  // ← Only English
  },
  
  themeConfig: {
    navbar: {
      title: "Agent Factory",
      hideOnScroll: false,
      items: [
        { to: "/factory", position: "left", label: "🏭 Factory" },
        { type: "docSidebar", sidebarId: "tutorialSidebar", position: "left", label: "Book" },
        { to: "/progress", position: "left", label: "Progress" },
        { to: "/leaderboard", position: "left", label: "Leaderboard" },
        { type: "custom-searchBar", position: "right" },
        { type: "custom-navbarAuth", position: "right" },
        // ❌ NO locale dropdown (not needed with single language)
      ],
    },
  },
};
```

**Status**: ✅ Correct for single language  
**Issue**: When multi-language is added, locale dropdown won't appear

---

## 🌍 WHEN ADDING FRENCH (Example)

### Step 1: Update i18n Config

**File**: `docusaurus.config.ts`

```typescript
// CHANGE THIS:
i18n: {
  defaultLocale: "en",
  locales: ["en"],
},

// TO THIS:
i18n: {
  defaultLocale: "en",
  locales: ["en", "fr"],  // ← Add French
  localeConfigs: {
    en: {
      label: "English",
      direction: "ltr",
      htmlLang: "en-US",
      calendar: "gregory",
      path: "en",
      translate: false,  // Already English
    },
    fr: {
      label: "Français",  // Show "Français" in dropdown
      direction: "ltr",
      htmlLang: "fr-FR",
      calendar: "gregory",
      path: "fr",
      translate: true,  // Run translation process
    },
  },
},
```

### Step 2: Add Locale Dropdown to Navbar

**File**: `docusaurus.config.ts`

```typescript
// NAVBAR ITEMS - ADD THIS:
navbar: {
  title: "Agent Factory",
  hideOnScroll: false,
  items: [
    { to: "/factory", position: "left", label: "🏭 Factory" },
    { type: "docSidebar", sidebarId: "tutorialSidebar", position: "left", label: "Book" },
    { to: "/progress", position: "left", label: "Progress" },
    { to: "/leaderboard", position: "left", label: "Leaderboard" },
    
    // ✅ ADD THIS ITEM:
    {
      type: "localeDropdown",
      position: "right",
      dropdownItemsAfter: [
        {
          href: "https://github.com/panaversity/...",
          label: "Help us translate",
        },
      ],
    },
    
    { type: "custom-searchBar", position: "right" },
    { type: "custom-navbarAuth", position: "right" },
  ],
},
```

### Step 3: Extract Translation Keys

```bash
# Command to run ONCE when adding new locale
npm run write-translations -- --locale fr
```

This creates the file structure:
```
i18n/
├── fr/
│   ├── docusaurus-theme-classic/
│   │   ├── navbar.json        ← Navbar labels in French
│   │   └── footer.json        ← Footer labels in French
│   ├── docusaurus-plugin-content-docs/
│   │   └── current/           ← French docs (copy from docs/, translate)
│   │       ├── 01-General-Agents-Foundations/
│   │       ├── 02-Agent-Workflow-Primitives/
│   │       └── ... (all chapters)
│   └── code.json              ← React component text in French
```

### Step 4: Navbar Translation File

**File**: `i18n/fr/docusaurus-theme-classic/navbar.json`

```json
{
  "title": {
    "message": "Agent Factory",
    "description": "Navbar title"
  },
  
  "item.label.Factory": {
    "message": "🏭 Usine",
    "description": "Navigation item label for factory page"
  },
  
  "item.label.Book": {
    "message": "📚 Livre",
    "description": "Navigation item label for documentation"
  },
  
  "item.label.Progress": {
    "message": "Progression",
    "description": "Navigation item label for progress tracking"
  },
  
  "item.label.Leaderboard": {
    "message": "Classement",
    "description": "Navigation item label for leaderboard"
  }
}
```

### Step 5: Test

```bash
# Start with French locale to test
npm run start -- --locale fr

# Should see:
# - URL: http://localhost:3000/fr/
# - Navbar dropdown showing: English, Français
# - All labels in French
```

---

## 📁 FILE STRUCTURE FOR MULTI-LANGUAGE

### Current Structure (English Only)

```
apps/learn-app/
├── docs/
│   ├── 01-General-Agents-Foundations/
│   ├── 02-Agent-Workflow-Primitives/
│   ├── ... (all chapters in English)
│   ├── thesis.md
│   └── whats-new.md
└── docusaurus.config.ts
```

### With French Added

```
apps/learn-app/
├── docs/                    ← English (default)
│   ├── 01-General-Agents-Foundations/
│   ├── 02-Agent-Workflow-Primitives/
│   ├── ... (all chapters)
│   ├── thesis.md
│   └── whats-new.md
│
├── i18n/                    ← NEW: Translation files
│   └── fr/                  ← Each locale gets a folder
│       ├── docusaurus-theme-classic/
│       │   ├── navbar.json  ← Navbar labels
│       │   └── footer.json  ← Footer labels
│       │
│       ├── docusaurus-plugin-content-docs/
│       │   └── current/     ← Translated docs
│       │       ├── 01-General-Agents-Foundations/
│       │       ├── 02-Agent-Workflow-Primitives/
│       │       ├── ... (translated versions of all docs)
│       │       ├── thesis.md  (in French)
│       │       └── whats-new.md (in French)
│       │
│       └── code.json        ← React text translations
│
└── docusaurus.config.ts
```

---

## 🔄 LOCALE SWITCHING FLOW (Official Docusaurus)

### User Clicks Locale Dropdown

```
User clicks "Français" in dropdown
    ↓
Docusaurus navigates to /fr/{current-page}
    ↓
Browser loads French version:
  - i18n/fr/docusaurus-theme-classic/navbar.json
  - i18n/fr/docusaurus-plugin-content-docs/current/...
  - i18n/fr/code.json
    ↓
Page renders in French
```

### URL Examples

| Action | URL | Language |
|--------|-----|----------|
| Visit home | `/` | English (default) |
| Visit docs | `/docs/thesis` | English |
| Switch to French | `/fr/` | French |
| Visit French docs | `/fr/docs/thesis` | French |
| Switch back to English | `/docs/thesis` | English |

---

## 🎯 NAVBAR DROPDOWN BEHAVIOR

### With One Language (Current)

```
No dropdown shown - only "en" exists
```

### With Two Languages

```
┌─────────────────┐
│ 📍 English      │  ← Current locale
│ 🇫🇷 Français   │  ← Click to switch
├─────────────────┤
│ Help us          │  ← Optional link
│ translate        │
└─────────────────┘
```

### Custom Item Position

```typescript
// Navbar items ORDER matters for right-side items

items: [
  { position: "left", ... },   // These appear left-to-right
  { position: "right", ... },  // These appear right-to-left!
  { position: "right", ... },  // So rightmost item defined last
]

// Results in navbar like:
// [Left Items] ← [Right Item 3] [Right Item 2] [Right Item 1] →
```

**For Agent Factory:**
```typescript
items: [
  // LEFT SIDE
  { label: "Factory", position: "left" },
  { label: "Book", position: "left" },
  { label: "Progress", position: "left" },
  { label: "Leaderboard", position: "left" },
  
  // RIGHT SIDE (in reverse visual order!)
  { type: "custom-navbarAuth", position: "right" },  ← Appears rightmost
  { type: "custom-searchBar", position: "right" },   ← Middle right
  { type: "localeDropdown", position: "right" },     ← Leftmost of right items
]

// Visual order: Factory Book Progress Leaderboard [Locale] [Search] [Auth]
```

---

## 🚀 BUILD & DEPLOY

### Build Single Locale

```bash
# Build only French
npm run build -- --locale fr

# Output: build/index.html (without /fr/ prefix)
# Deploy to: https://fr.example.com
```

### Build All Locales

```bash
# Build English + French
npm run build

# Output:
# - build/index.html          (English)
# - build/fr/index.html       (French)
# Deploy to: https://example.com
```

### Deployment Strategies

#### Strategy 1: Single Domain (Recommended for Agent Factory)

```
https://agentfactory.panaversity.org/
├── /              → English
├── /fr/           → French
├── /docs/thesis   → English
└── /fr/docs/thesis → French

# Configuration:
i18n: {
  defaultLocale: "en",
  locales: ["en", "fr"],
  # Default baseUrl handling works
}
```

#### Strategy 2: Multi-Domain

```
https://en.agentfactory.panaversity.org/
├── /              → English version
└── /docs/thesis   → English docs

https://fr.agentfactory.panaversity.org/
├── /              → French version
└── /docs/thesis   → French docs

# Configuration:
i18n: {
  defaultLocale: "en",
  locales: ["en", "fr"],
  localeConfigs: {
    en: {
      url: "https://en.agentfactory.panaversity.org",
      baseUrl: "/",
    },
    fr: {
      url: "https://fr.agentfactory.panaversity.org",
      baseUrl: "/",
    },
  },
}
```

---

## ⚠️ IMPORTANT NOTES FOR AGENT FACTORY

### Custom Navbar Components

Agent Factory uses custom components:
- `type: "custom-searchBar"` ← Custom search implementation
- `type: "custom-navbarAuth"` ← Custom auth (OAuth, user menu)

These **don't need translation** because they're:
1. Low-text components
2. Auth-specific (handled by SSO auth service)
3. Search is language-generic

### RTL Language Support

If adding Arabic/Hebrew/Persian:

```typescript
fa: {
  label: "فارسی",
  direction: "rtl",  // ← Automatic RTL layout
  htmlLang: "fa-IR",
}
```

Docusaurus automatically:
- Flips navbar (RTL layout)
- Flips sidebar navigation
- Sets `dir="rtl"` on `<html>`

### When Translation is NOT Needed

You DON'T need `localeDropdown` if:
- Only supporting English
- Using automatic translation tools (not recommended)
- Supporting one language per deployment

---

## ✅ CHECKLIST FOR ADDING FRENCH

- [ ] Update `i18n.locales` to include `"fr"`
- [ ] Add `localeConfigs.fr` configuration
- [ ] Add `localeDropdown` item to navbar
- [ ] Run `npm run write-translations -- --locale fr`
- [ ] Translate `i18n/fr/docusaurus-theme-classic/navbar.json`
- [ ] Translate `i18n/fr/docusaurus-theme-classic/footer.json`
- [ ] Translate or copy `docs/` to `i18n/fr/docusaurus-plugin-content-docs/current/`
- [ ] Fill `i18n/fr/code.json` with French translations
- [ ] Test with `npm run start -- --locale fr`
- [ ] Test URL switching between locales
- [ ] Verify locale button appears in navbar
- [ ] Build and verify: `npm run build`

---

## 📚 OFFICIAL DOCUSAURUS REFERENCES

1. **Navbar Configuration**
   - https://docusaurus.io/docs/api/themes/configuration#navbar
   - Full navbar items reference
   - All `type:` options documented

2. **Internationalization (i18n)**
   - https://docusaurus.io/docs/i18n/introduction
   - Complete i18n system explanation
   - Translation workflow

3. **i18n Tutorial**
   - https://docusaurus.io/docs/i18n/tutorial
   - Step-by-step multi-language setup
   - Deployment strategies

4. **Locale Dropdown Specific**
   - https://docusaurus.io/docs/api/themes/configuration#navbar-locale-dropdown
   - All options for `type: "localeDropdown"`
   - Query string persistence example

---

**Document prepared**: February 22, 2026  
**For**: Agent Factory Project  
**Docusaurus Version**: 3.9.2  
**Current Language Support**: English Only
