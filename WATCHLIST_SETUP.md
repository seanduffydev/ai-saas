# Watchlist Feature Setup Guide

This guide will help you set up the new customizable watchlist feature for your Commodity Forecasting Lab application.

## Overview

The watchlist feature has been enhanced to allow users to:
- ✅ Add any commodity to their personal watchlist
- ✅ Remove commodities from their watchlist
- ✅ Persist watchlist preferences in the database
- ✅ Automatically initialize with Gold, Silver, and Crude Oil as defaults

## Setup Steps

### 1. Create Database Table in Supabase

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Click **New Query**
4. Copy and paste the contents of `backend/database/schema.sql`
5. Click **Run** to execute the SQL

This will create:
- `watchlist_preferences` table with proper constraints and indexes
- Row Level Security (RLS) policies for user data protection
- Helper function `initialize_default_watchlist()` for new users

### 2. Verify Table Creation

After running the SQL, verify the table was created:

1. Go to **Table Editor** in Supabase
2. Look for `watchlist_preferences` table
3. You should see these columns:
   - `id` (UUID, primary key)
   - `user_id` (UUID, foreign key to auth.users)
   - `commodity_id` (VARCHAR)
   - `order_index` (INTEGER)
   - `added_at` (TIMESTAMP)

### 3. Test the Feature

The feature is now ready to use! Here's what happens:

**For New Users:**
- When a user first visits the dashboard, the app checks if they have watchlist items
- If not, it automatically initializes with: Gold, Silver, Crude Oil
- These defaults are stored in the database

**For Existing Users:**
- The app will load their saved watchlist preferences
- If they have no saved preferences, defaults will be initialized

## API Endpoints

The following new endpoints are available:

### GET /api/watchlist
Get user's watchlist commodities
```
Query params: user_id
Response: Array of watchlist items ordered by order_index
```

### POST /api/watchlist
Add a commodity to watchlist
```
Query params: user_id
Body: { "commodity_id": "gold" }
Response: Success message with created item
```

### DELETE /api/watchlist/{commodity_id}
Remove a commodity from watchlist
```
Query params: user_id
Response: Success message
```

### POST /api/watchlist/initialize
Initialize default watchlist for new user
```
Query params: user_id
Response: Success message with default items (gold, silver, crude_oil)
```

## Frontend Changes

The `Watchlist` component has been updated with:

### New Features:
- **Add Modal**: Click "+ Add to Watchlist" to see available commodities
- **Remove Buttons**: Each commodity has an "✕" button to remove it
- **Empty State**: Shows helpful message when watchlist is empty
- **Persistence**: All changes are saved to Supabase immediately

### UI Improvements:
- Beautiful modal with grid layout of commodity cards
- Hover effects on commodity cards
- Disable "Add" button when all commodities are added
- Confirmation dialog before removing commodities

## Available Commodities

Users can add any of these commodities to their watchlist:

| ID | Name | Category | Icon |
|----|------|----------|------|
| gold | Gold | Metals | 🥇 |
| silver | Silver | Metals | 🥈 |
| crude_oil | Crude Oil (WTI) | Energy | 🛢️ |
| natural_gas | Natural Gas | Energy | ⚡ |
| copper | Copper | Metals | 🔶 |
| wheat | Wheat | Agriculture | 🌾 |
| corn | Corn | Agriculture | 🌽 |
| soybeans | Soybeans | Agriculture | 🫘 |

## Security

Row Level Security (RLS) is enabled on the `watchlist_preferences` table:
- Users can only view their own watchlist items
- Users can only insert/update/delete their own items
- All queries are filtered by `user_id` to prevent data leaks

## Troubleshooting

### Issue: "Table does not exist" error
**Solution:** Run the SQL schema file in Supabase SQL Editor

### Issue: Permission denied when accessing watchlist
**Solution:** Check that RLS policies were created properly. Re-run the schema.sql file.

### Issue: Watchlist not initializing for new users
**Solution:** Check the browser console for errors. Verify the API endpoint is accessible.

### Issue: Can't remove items from watchlist
**Solution:** Ensure the user_id is being passed correctly in the DELETE request.

## Testing Checklist

- [ ] New user sees Gold, Silver, Crude Oil by default
- [ ] Can add a commodity via the modal
- [ ] Can remove a commodity with the ✕ button
- [ ] Watchlist persists after page refresh
- [ ] Can add all commodities to watchlist
- [ ] "Add" button disabled when all commodities added
- [ ] Can remove all commodities (empty state shows)
- [ ] Modal closes when clicking outside
- [ ] Duplicate commodity shows error message

## Next Steps

With the basic functionality working, you can consider these enhancements:
- Drag-and-drop reordering (update `order_index`)
- Price alerts (add threshold columns)
- Watchlist presets (Metal Pack, Energy Pack, etc.)
- Export/share watchlist functionality
- Mini sparkline charts for each commodity

---

**Questions?** Check the implementation in:
- Backend: `backend/app/main.py` (lines 548-625)
- Frontend: `frontend/src/components/dashboard/Watchlist.jsx`
- Database: `backend/database/schema.sql`
