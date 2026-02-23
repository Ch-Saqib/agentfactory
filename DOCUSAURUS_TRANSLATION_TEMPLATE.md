# Agent Factory docusaurus.config.ts - Translation-Ready Template

**Purpose**: Show exact code changes needed to add translation support  
**Current Status**: Single language (English) ✅ Working correctly  
**When to Use**: Reference when adding French, Spanish, or other languages  

---

## 📋 CURRENT v3.9.2 CONFIG (ENGLISH ONLY)

```typescript
// docusaurus.config.ts - CURRENT STATE

// Locale only supports English
i18n: {
  defaultLocale: "en",
  locales: ["en"],  // ← ONLY English
},

// Navbar - No locale dropdown because only 1 language
navbar: {
  title: "Agent Factory",
  hideOnScroll: false,
  items: [
    { to: "/factory", position: "left", label: "🏭 Factory", className: "navbar-factory-link" },
    { type: "docSidebar", sidebarId: "tutorialSidebar", position: "left", label: "Book" },
    { to: "/progress", position: "left", label: "Progress" },
    { to: "/leaderboard", position: "left", label: "Leaderboard" },
    { type: "custom-searchBar", position: "right" },
    { type: "custom-navbarAuth", position: "right" },
    // ❌ NO localeDropdown (not needed with single language)
  ],
},
```

**Status**: ✅ **CORRECT** - No changes needed for single language

---

## 🌍 TRANSLATION-READY TEMPLATE (MULTI-LANGUAGE)

### Template for When Adding Languages

```typescript
// docusaurus.config.ts - TRANSLATION-READY VERSION

// ============================================================
// CONFIGURATION 1: i18n (Internationalization)
// ============================================================

i18n: {
  // The locale that will NOT have a prefix in URLs
  defaultLocale: "en",
  
  // All supported locales
  locales: ["en", "fr"],  // ← ADD languages here
  
  // Root folder for all translation files
  path: "i18n",
  
  // Per-language configuration
  localeConfigs: {
    // ALWAYS define the default locale
    en: {
      label: "English",           // Shown in locale dropdown
      direction: "ltr",           // Left-to-right
      htmlLang: "en-US",          // HTML lang attribute
      calendar: "gregory",        // Gregorian calendar
      path: "en",                 // Folder name
      translate: false,           // Already in English - no translation needed
    },
    
    // ============================================================
    // ADD NEW LOCALES HERE (Example: French)
    // ============================================================
    // fr: {
    //   label: "Français",        // Shown in locale dropdown
    //   direction: "ltr",         // Left-to-right
    //   htmlLang: "fr-FR",        // HTML lang attribute
    //   calendar: "gregory",      // Gregorian calendar
    //   path: "fr",               // Folder name (i18n/fr/)
    //   translate: true,          // Run translation process
    // },
    
    // Example: Spanish
    // es: {
    //   label: "Español",
    //   direction: "ltr",
    //   htmlLang: "es-ES",
    //   calendar: "gregory",
    //   path: "es",
    //   translate: true,
    // },
    
    // Example: Right-to-Left language (Arabic)
    // ar: {
    //   label: "العربية",        // Arabic label
    //   direction: "rtl",         // Right-to-left ← KEY: RTL layout
    //   htmlLang: "ar",
    //   calendar: "islamic",      // Islamic calendar optional
    //   path: "ar",
    //   translate: true,
    // },
  },
},

// ============================================================
// CONFIGURATION 2: Navbar (Navigation Bar)
// ============================================================

navbar: {
  title: "Agent Factory",
  hideOnScroll: false,
  items: [
    // LEFT SIDE ITEMS
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
    
    // RIGHT SIDE ITEMS
    // ============================================================
    // LOCALE DROPDOWN (Translation Button)
    // ============================================================
    // UNCOMMENT THIS when adding multiple locales
    // {
    //   type: "localeDropdown",
    //   position: "right",
    //   dropdownItemsAfter: [
    //     {
    //       to: "https://github.com/panaversity/ai-native-software-development",
    //       label: "Help us translate",
    //     },
    //   ],
    // },
    
    // Search bar
    {
      type: "custom-searchBar",
      position: "right",
    },
    
    // Auth/Login dropdown
    {
      type: "custom-navbarAuth",
      position: "right",
    },
  ],
},
```

---

## 🔄 STEP-BY-STEP: ADD FRENCH

### Step 1: Uncomment French in i18n

**In** `docusaurus.config.ts`:

```typescript
// CHANGE THIS:
locales: ["en"],

// TO THIS:
locales: ["en", "fr"],

// AND uncomment fr config:
// fr: {
//   label: "Français",
//   direction: "ltr",
//   htmlLang: "fr-FR",
//   calendar: "gregory",
//   path: "fr",
//   translate: true,
// },

// BECOMES:
fr: {
  label: "Français",
  direction: "ltr",
  htmlLang: "fr-FR",
  calendar: "gregory",
  path: "fr",
  translate: true,
},
```

### Step 2: Uncomment Locale Dropdown in Navbar

**In** `docusaurus.config.ts`:

```typescript
// UNCOMMENT THIS BLOCK:
// {
//   type: "localeDropdown",
//   position: "right",
//   dropdownItemsAfter: [
//     {
//       to: "https://github.com/panaversity/ai-native-software-development",
//       label: "Help us translate",
//     },
//   ],
// },

// NOW:
{
  type: "localeDropdown",
  position: "right",
  dropdownItemsAfter: [
    {
      to: "https://github.com/panaversity/ai-native-software-development",
      label: "Help us translate",
    },
  ],
},
```

### Step 3: Run Write Translations Command

```bash
npm run write-translations -- --locale fr
```

This generates:
```
i18n/fr/
├── docusaurus-theme-classic/
│   ├── navbar.json    ← Fill with French translations
│   └── footer.json    ← Fill with French translations
├── docusaurus-plugin-content-docs/
│   └── current/       ← Copy & translate docs here
└── code.json          ← Fill with French translations
```

### Step 4: Test Locally

```bash
# Start development server with French
npm run start -- --locale fr

# Visit: http://localhost:3000/fr/
# Should see dropdown, French navbar labels, etc.
```

---

## 📝 TRANSLATION FILES STRUCTURE

After running `write-translations`, these files are created:

### 1. Navbar Labels

**File**: `i18n/fr/docusaurus-theme-classic/navbar.json`

```json
{
  "item.label.Factory": {
    "message": "🏭 Usine",
    "description": "Navbar label for factory page"
  },
  "item.label.Book": {
    "message": "📚 Livre",
    "description": "Navbar label for book/docs"
  },
  "item.label.Progress": {
    "message": "Progression",
    "description": "Navbar label for progress tracking"
  },
  "item.label.Leaderboard": {
    "message": "Classement",
    "description": "Navbar label for leaderboard"
  }
}
```

### 2. Footer Labels

**File**: `i18n/fr/docusaurus-theme-classic/footer.json`

```json
{
  "title.Learn": {
    "message": "Apprendre",
    "description": "Footer section title"
  },
  "item.label.GitHub": {
    "message": "Dépôt GitHub",
    "description": "Footer social link"
  }
  // ... fill as needed
}
```

### 3. React Component Text

**File**: `i18n/fr/code.json`

```json
{
  "Welcome to Agent Factory": {
    "message": "Bienvenue à Agent Factory",
    "description": "Home page welcome"
  },
  "Learn to build AI": {
    "message": "Apprenez à construire des IA",
    "description": "Home page subtitle"
  }
  // ... fill as needed
}
```

### 4. Documentation Pages

**Structure**: `i18n/fr/docusaurus-plugin-content-docs/current/`

```bash
# Copy English docs to French folder and translate
cp -r docs/* i18n/fr/docusaurus-plugin-content-docs/current/

# Then translate each file:
# i18n/fr/docusaurus-plugin-content-docs/current/
# ├── 01-General-Agents-Foundations/
# ├── 02-Agent-Workflow-Primitives/
# ├── ... (all chapters in French)
# ├── thesis.md (translated)
# └── whats-new.md (translated)
```

---

## 🌐 SUPPORTING MORE LANGUAGES

### Adding Spanish

```typescript
locales: ["en", "fr", "es"],

localeConfigs: {
  // ... en, fr ...
  
  es: {
    label: "Español",
    direction: "ltr",
    htmlLang: "es-ES",
    calendar: "gregory",
    path: "es",
    translate: true,
  },
},
```

### Adding Right-to-Left Language (Arabic)

```typescript
locales: ["en", "fr", "ar"],

localeConfigs: {
  // ... en, fr ...
  
  ar: {
    label: "العربية",        // Arabic label (حروف عربية)
    direction: "rtl",         // ← IMPORTANT: Right-to-left
    htmlLang: "ar",
    calendar: "islamic",      // Islamic calendar system
    path: "ar",
    translate: true,
  },
},
```

### Adding Persian

```typescript
fa: {
  label: "فارسی",            // Persian label
  direction: "rtl",
  htmlLang: "fa-IR",
  calendar: "persian",        // Persian calendar
  path: "fa",
  translate: true,
},
```

---

## ⚡ QUICK COMMANDS

```bash
# Extract translation keys when adding new language
npm run write-translations -- --locale fr

# Start dev server for specific locale
npm run start -- --locale fr

# Build single locale (for multi-domain deployment)
npm run build -- --locale fr

# Build all locales
npm run build

# List all available locales
grep -A 20 "locales:" docusaurus.config.ts
```

---

## 🎯 DECISION FLOWCHART

```
Do you need multiple languages?
│
├─ NO → Keep current setup:
│       locales: ["en"]
│       No localeDropdown in navbar
│       ✅ All working
│
└─ YES → Make changes:
         ├─ Add locales to i18n: ["en", "fr", ...]
         ├─ Define localeConfigs for each
         ├─ Add localeDropdown to navbar
         ├─ Run: npm run write-translations -- --locale fr
         ├─ Translate: i18n/fr/*.json
         ├─ Translate: i18n/fr/docusaurus-plugin-content-docs/
         ├─ Test: npm run start -- --locale fr
         └─ Build: npm run build
```

---

## ✅ FINAL CHECKLIST FOR ADDING NEW LANGUAGE

- [ ] Add locale to `locales` array
- [ ] Add locale configuration in `localeConfigs`
- [ ] Uncomment/add `localeDropdown` in navbar items
- [ ] Run `npm run write-translations -- --locale {code}`
- [ ] Create `i18n/{code}/docusaurus-theme-classic/navbar.json`
- [ ] Create `i18n/{code}/docusaurus-theme-classic/footer.json`
- [ ] Create `i18n/{code}/code.json` (React text)
- [ ] Copy docs to `i18n/{code}/docusaurus-plugin-content-docs/current/`
- [ ] Translate all JSON files
- [ ] Translate all Markdown files
- [ ] Test with `npm run start -- --locale {code}`
- [ ] Verify locale dropdown works
- [ ] Deploy!

---

## 📚 REFERENCE FILES THIS USES

- **config**: `apps/learn-app/docusaurus.config.ts`
- **theme**: Uses `@docusaurus/preset-classic`
- **default locale navbar labels**: English
- **translation files location**: `apps/learn-app/i18n/`

---

**Template last updated**: February 22, 2026  
**Docusaurus version**: 3.9.2  
**Ready for**: English + any languages you want to add
