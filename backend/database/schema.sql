-- Watchlist Preferences Table
-- This table stores user-specific watchlist commodities with ordering

CREATE TABLE IF NOT EXISTS watchlist_preferences (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    commodity_id VARCHAR(50) NOT NULL,
    order_index INTEGER NOT NULL DEFAULT 0,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Ensure a user doesn't add the same commodity twice
    UNIQUE(user_id, commodity_id)
);

-- Index for faster queries by user_id
CREATE INDEX IF NOT EXISTS idx_watchlist_user_id ON watchlist_preferences(user_id);

-- Index for ordering
CREATE INDEX IF NOT EXISTS idx_watchlist_order ON watchlist_preferences(user_id, order_index);

-- Enable Row Level Security
ALTER TABLE watchlist_preferences ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own watchlist items
CREATE POLICY "Users can view their own watchlist"
    ON watchlist_preferences
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users can insert their own watchlist items
CREATE POLICY "Users can insert their own watchlist"
    ON watchlist_preferences
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own watchlist items
CREATE POLICY "Users can update their own watchlist"
    ON watchlist_preferences
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Policy: Users can delete their own watchlist items
CREATE POLICY "Users can delete their own watchlist"
    ON watchlist_preferences
    FOR DELETE
    USING (auth.uid() = user_id);

-- Function to initialize default watchlist for new users
-- This can be called via a trigger or manually when a user signs up
CREATE OR REPLACE FUNCTION initialize_default_watchlist(p_user_id UUID)
RETURNS void AS $$
BEGIN
    -- Insert default commodities: Gold, Silver, Crude Oil
    INSERT INTO watchlist_preferences (user_id, commodity_id, order_index)
    VALUES
        (p_user_id, 'gold', 0),
        (p_user_id, 'silver', 1),
        (p_user_id, 'crude_oil', 2)
    ON CONFLICT (user_id, commodity_id) DO NOTHING;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Optional: Trigger to auto-initialize watchlist for new users
-- Uncomment if you want automatic initialization
-- CREATE OR REPLACE FUNCTION auto_initialize_watchlist()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     PERFORM initialize_default_watchlist(NEW.id);
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql SECURITY DEFINER;

-- CREATE TRIGGER on_user_created
--     AFTER INSERT ON auth.users
--     FOR EACH ROW
--     EXECUTE FUNCTION auto_initialize_watchlist();
