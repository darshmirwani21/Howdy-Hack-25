# Quick Start Guide

## 🚀 Get Running in 2 Minutes

### 1. Setup (30 seconds)
```bash
# Install dependencies
npm install

# Add your OpenAI API key
echo "OPENAI_API_KEY=sk-your-actual-key" > .env
```

Get an OpenAI API key: https://platform.openai.com/api-keys

### 2. Test CLI (30 seconds)
```bash
node index.js --url "https://example.com" --prompt "Scroll down"
```

Expected output:
- Browser opens automatically
- Action executes
- Screenshot saved to `./screenshots/`
- Results printed to console
- JSON file created: `test-results-{timestamp}.json`

### 3. Launch UI (1 minute)
```bash
npm run ui
```

Then:
1. Enter URL: `https://example.com`
2. Enter prompt: `Scroll down. Click more information`
3. Click "Run Test"
4. Watch the magic happen! ✨

## 📖 Example Prompts

### Simple
```
Scroll to bottom
```

### Multi-Step
```
Navigate to login. Fill username with test@example.com. Click submit
```

### Complex
```
Search for laptop. Wait for results. Click first item. Add to cart. Go to checkout
```

## 🎯 Common Use Cases

### Test a Login Form
```bash
node index.js --url "http://localhost:3000" --prompt "Click login button. Fill email with test@test.com. Fill password with pass123. Click submit"
```

### Test Navigation
```bash
node index.js --url "http://localhost:3000" --prompt "Click About link. Scroll to team section. Click contact button"
```

### Test Form Validation
```bash
node index.js --url "http://localhost:3000" --prompt "Click submit without filling form. Verify error messages appear"
```

## 🐛 Troubleshooting

### "OPENAI_API_KEY not found"
→ Create `.env` file with your API key

### "Element not found"
→ Be more specific in your prompt (e.g., "Click the blue submit button")

### Browser doesn't open
→ Check if Playwright browsers are installed: `npx playwright install chromium`

### Electron UI won't start
→ Run `npm install` to ensure Electron is installed

## 📚 Learn More

- Full documentation: [TESTING_GUIDE.md](./TESTING_GUIDE.md)
- Implementation details: [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
- Stagehand docs: https://docs.stagehand.dev

## 💡 Pro Tips

1. **Period = New Action**: Each sentence (ending with `.`) becomes a separate action
2. **Be Specific**: Reference visible text on the page
3. **Check Screenshots**: Look at `./screenshots/` to see what the AI saw
4. **Use Verbose**: Add `--verbose` flag for detailed logs
5. **UI for Demos**: Use `npm run ui` for impressive visual demos

## 🎓 Hackathon Demo Script

```bash
# 1. Start your web app
npm run dev  # or whatever starts your app on port 3000

# 2. Open the UI in another terminal
npm run ui

# 3. Demo the testing
# Enter: http://localhost:3000
# Enter: Navigate to signup. Fill all fields. Submit form
# Click: Run Test

# 4. Show the results
# - Live action feed
# - Screenshots
# - Success/failure summary
```

## 🤝 Cursor Integration

Add this to your Cursor workflow:

```bash
# After making UI changes, run:
node index.js --url "http://localhost:3000" --prompt "Test the new feature"
```

Cursor will read the results and suggest improvements!

---

**Need help?** Check the full [TESTING_GUIDE.md](./TESTING_GUIDE.md)

