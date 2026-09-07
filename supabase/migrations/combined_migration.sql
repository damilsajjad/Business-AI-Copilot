-- ============================================================
-- AI Business Copilot — Complete Production Migration
-- Creates all tables, triggers, and Row Level Security policies
-- Generated with proper dependency ordering.
-- ============================================================

-- ============================================================
-- STEP 1: CREATE ALL TABLES
-- ============================================================

-- 1. Profiles (linked to Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email text NOT NULL,
    full_name text DEFAULT '',
    avatar_url text DEFAULT '',
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);

-- 2. Businesses (multi-tenant workspace)
CREATE TABLE IF NOT EXISTS public.businesses (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    industry text DEFAULT '',
    description text DEFAULT '',
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);

-- 3. Business Memberships (RBAC mapping)
CREATE TABLE IF NOT EXISTS public.business_memberships (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id uuid NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role text NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'member')),
    created_at timestamptz DEFAULT now() NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_business_memberships_unique ON public.business_memberships(business_id, user_id);
CREATE INDEX IF NOT EXISTS idx_business_memberships_user ON public.business_memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_business_memberships_business ON public.business_memberships(business_id);

-- 4. Uploaded Files
CREATE TABLE IF NOT EXISTS public.uploaded_files (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id uuid NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    uploaded_by uuid NOT NULL REFERENCES auth.users(id) ON DELETE SET NULL,
    original_filename text NOT NULL,
    storage_path text NOT NULL,
    file_type text NOT NULL CHECK (file_type IN ('csv', 'xlsx')),
    file_size_bytes bigint NOT NULL DEFAULT 0,
    status text NOT NULL DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'profiling', 'profiled', 'mapping', 'mapped', 'processing', 'ready', 'error')),
    sheet_count integer DEFAULT 1,
    error_message text DEFAULT '',
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_uploaded_files_business ON public.uploaded_files(business_id);
CREATE INDEX IF NOT EXISTS idx_uploaded_files_status ON public.uploaded_files(status);
CREATE INDEX IF NOT EXISTS idx_uploaded_files_uploaded_by ON public.uploaded_files(uploaded_by);

-- 5. Data Mappings
CREATE TABLE IF NOT EXISTS public.data_mappings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id uuid NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    file_id uuid NOT NULL REFERENCES public.uploaded_files(id) ON DELETE CASCADE,
    mappings jsonb NOT NULL DEFAULT '[]'::jsonb,
    status text NOT NULL DEFAULT 'confirmed' CHECK (status IN ('draft', 'confirmed')),
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_data_mappings_business_file ON public.data_mappings(business_id, file_id);
CREATE INDEX IF NOT EXISTS idx_data_mappings_file ON public.data_mappings(file_id);

-- 6. Analytics Results
CREATE TABLE IF NOT EXISTS public.analytics_results (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id uuid NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    file_id uuid NOT NULL REFERENCES public.uploaded_files(id) ON DELETE CASCADE,
    results jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_analytics_results_business_file ON public.analytics_results(business_id, file_id);
CREATE INDEX IF NOT EXISTS idx_analytics_results_file ON public.analytics_results(file_id);

-- 7. ML Forecasts
CREATE TABLE IF NOT EXISTS public.ml_forecasts (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id uuid NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    file_id uuid NOT NULL REFERENCES public.uploaded_files(id) ON DELETE CASCADE,
    forecast_type text NOT NULL CHECK (forecast_type IN ('sales', 'churn')),
    results jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_ml_forecasts_lookup ON public.ml_forecasts(business_id, file_id, forecast_type);

-- 8. AI Insights
CREATE TABLE IF NOT EXISTS public.ai_insights (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id uuid NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    file_id uuid NOT NULL REFERENCES public.uploaded_files(id) ON DELETE CASCADE,
    insights jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_ai_insights_lookup ON public.ai_insights(business_id, file_id);

-- 9. Copilot Messages
CREATE TABLE IF NOT EXISTS public.copilot_messages (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id uuid NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    file_id uuid NOT NULL REFERENCES public.uploaded_files(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role text NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content text NOT NULL,
    context jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now() NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_copilot_messages_lookup ON public.copilot_messages(business_id, file_id, created_at ASC);

-- 10. Action Items
CREATE TABLE IF NOT EXISTS public.action_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id uuid NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    file_id uuid NOT NULL REFERENCES public.uploaded_files(id) ON DELETE CASCADE,
    title text NOT NULL,
    domain text NOT NULL,
    urgency text NOT NULL CHECK (urgency IN ('high', 'medium', 'low')),
    expected_impact text NOT NULL,
    effort text NOT NULL CHECK (effort IN ('low', 'medium', 'high')),
    timeframe text NOT NULL,
    action_steps jsonb NOT NULL DEFAULT '[]'::jsonb,
    owner text NOT NULL DEFAULT 'Executive Team',
    risk_if_ignored text NOT NULL DEFAULT '',
    status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'dismissed')),
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_action_items_lookup ON public.action_items(business_id, file_id, status);

-- 11. Scheduled Reports
CREATE TABLE IF NOT EXISTS public.scheduled_reports (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id uuid NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    report_type text NOT NULL DEFAULT 'weekly' CHECK (report_type IN ('weekly', 'monthly')),
    status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused')),
    last_generated_at timestamptz,
    last_report_content jsonb DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_scheduled_reports_biz ON public.scheduled_reports(business_id, report_type);

-- ============================================================
-- STEP 2: ENABLE ROW LEVEL SECURITY
-- ============================================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.businesses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.business_memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.uploaded_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.data_mappings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analytics_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ml_forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.copilot_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.action_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scheduled_reports ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- STEP 3: FUNCTIONS AND TRIGGERS
-- ============================================================

CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = ''
AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (NEW.id, NEW.email, coalesce(NEW.raw_user_meta_data ->> 'full_name', ''));
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

DROP TRIGGER IF EXISTS profiles_updated_at ON public.profiles;
CREATE TRIGGER profiles_updated_at BEFORE UPDATE ON public.profiles FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS businesses_updated_at ON public.businesses;
CREATE TRIGGER businesses_updated_at BEFORE UPDATE ON public.businesses FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS uploaded_files_updated_at ON public.uploaded_files;
CREATE TRIGGER uploaded_files_updated_at BEFORE UPDATE ON public.uploaded_files FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS data_mappings_updated_at ON public.data_mappings;
CREATE TRIGGER data_mappings_updated_at BEFORE UPDATE ON public.data_mappings FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS analytics_results_updated_at ON public.analytics_results;
CREATE TRIGGER analytics_results_updated_at BEFORE UPDATE ON public.analytics_results FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS ml_forecasts_updated_at ON public.ml_forecasts;
CREATE TRIGGER ml_forecasts_updated_at BEFORE UPDATE ON public.ml_forecasts FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS ai_insights_updated_at ON public.ai_insights;
CREATE TRIGGER ai_insights_updated_at BEFORE UPDATE ON public.ai_insights FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS action_items_updated_at ON public.action_items;
CREATE TRIGGER action_items_updated_at BEFORE UPDATE ON public.action_items FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS scheduled_reports_updated_at ON public.scheduled_reports;
CREATE TRIGGER scheduled_reports_updated_at BEFORE UPDATE ON public.scheduled_reports FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- ============================================================
-- STEP 4: ROW LEVEL SECURITY POLICIES
-- ============================================================

-- Profiles
DROP POLICY IF EXISTS "Users can read own profile" ON public.profiles;
CREATE POLICY "Users can read own profile" ON public.profiles FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id) WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "Service role can insert profiles" ON public.profiles;
CREATE POLICY "Service role can insert profiles" ON public.profiles FOR INSERT WITH CHECK (true);

-- Businesses
DROP POLICY IF EXISTS "Members can read their businesses" ON public.businesses;
CREATE POLICY "Members can read their businesses" ON public.businesses FOR SELECT
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Authenticated users can create businesses" ON public.businesses;
CREATE POLICY "Authenticated users can create businesses" ON public.businesses FOR INSERT WITH CHECK (auth.role() = 'authenticated');

DROP POLICY IF EXISTS "Owners can update their businesses" ON public.businesses;
CREATE POLICY "Owners can update their businesses" ON public.businesses FOR UPDATE
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = id AND bm.user_id = auth.uid() AND bm.role = 'owner'));

DROP POLICY IF EXISTS "Owners can delete their businesses" ON public.businesses;
CREATE POLICY "Owners can delete their businesses" ON public.businesses FOR DELETE
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = id AND bm.user_id = auth.uid() AND bm.role = 'owner'));

-- Business Memberships
DROP POLICY IF EXISTS "Members can see memberships of their businesses" ON public.business_memberships;
CREATE POLICY "Members can see memberships of their businesses" ON public.business_memberships FOR SELECT
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = business_memberships.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Service role can insert memberships" ON public.business_memberships;
CREATE POLICY "Service role can insert memberships" ON public.business_memberships FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "Owners can delete memberships" ON public.business_memberships;
CREATE POLICY "Owners can delete memberships" ON public.business_memberships FOR DELETE
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = business_memberships.business_id AND bm.user_id = auth.uid() AND bm.role = 'owner'));

-- Uploaded Files
DROP POLICY IF EXISTS "Members can read files of their businesses" ON public.uploaded_files;
CREATE POLICY "Members can read files of their businesses" ON public.uploaded_files FOR SELECT
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = uploaded_files.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Members can upload files to their businesses" ON public.uploaded_files;
CREATE POLICY "Members can upload files to their businesses" ON public.uploaded_files FOR INSERT
    WITH CHECK (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = uploaded_files.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Service role can update files" ON public.uploaded_files;
CREATE POLICY "Service role can update files" ON public.uploaded_files FOR UPDATE USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Owners can delete files" ON public.uploaded_files;
CREATE POLICY "Owners can delete files" ON public.uploaded_files FOR DELETE
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = uploaded_files.business_id AND bm.user_id = auth.uid() AND bm.role = 'owner'));

-- Data Mappings
DROP POLICY IF EXISTS "Members can read mappings of their businesses" ON public.data_mappings;
CREATE POLICY "Members can read mappings of their businesses" ON public.data_mappings FOR SELECT
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = data_mappings.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Members can insert mappings for their businesses" ON public.data_mappings;
CREATE POLICY "Members can insert mappings for their businesses" ON public.data_mappings FOR INSERT
    WITH CHECK (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = data_mappings.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Members can update mappings for their businesses" ON public.data_mappings;
CREATE POLICY "Members can update mappings for their businesses" ON public.data_mappings FOR UPDATE
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = data_mappings.business_id AND bm.user_id = auth.uid()))
    WITH CHECK (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = data_mappings.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Owners can delete mappings" ON public.data_mappings;
CREATE POLICY "Owners can delete mappings" ON public.data_mappings FOR DELETE
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = data_mappings.business_id AND bm.user_id = auth.uid() AND bm.role = 'owner'));

-- Analytics Results
DROP POLICY IF EXISTS "Members can read analytics of their businesses" ON public.analytics_results;
CREATE POLICY "Members can read analytics of their businesses" ON public.analytics_results FOR SELECT
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = analytics_results.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Members can insert analytics for their businesses" ON public.analytics_results;
CREATE POLICY "Members can insert analytics for their businesses" ON public.analytics_results FOR INSERT
    WITH CHECK (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = analytics_results.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Members can update analytics for their businesses" ON public.analytics_results;
CREATE POLICY "Members can update analytics for their businesses" ON public.analytics_results FOR UPDATE
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = analytics_results.business_id AND bm.user_id = auth.uid()))
    WITH CHECK (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = analytics_results.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Owners can delete analytics" ON public.analytics_results;
CREATE POLICY "Owners can delete analytics" ON public.analytics_results FOR DELETE
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = analytics_results.business_id AND bm.user_id = auth.uid() AND bm.role = 'owner'));

-- ML Forecasts
DROP POLICY IF EXISTS "Members can read forecasts of their businesses" ON public.ml_forecasts;
CREATE POLICY "Members can read forecasts of their businesses" ON public.ml_forecasts FOR SELECT
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = ml_forecasts.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Members can insert forecasts for their businesses" ON public.ml_forecasts;
CREATE POLICY "Members can insert forecasts for their businesses" ON public.ml_forecasts FOR INSERT
    WITH CHECK (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = ml_forecasts.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Members can update forecasts for their businesses" ON public.ml_forecasts;
CREATE POLICY "Members can update forecasts for their businesses" ON public.ml_forecasts FOR UPDATE
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = ml_forecasts.business_id AND bm.user_id = auth.uid()))
    WITH CHECK (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = ml_forecasts.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Owners can delete forecasts" ON public.ml_forecasts;
CREATE POLICY "Owners can delete forecasts" ON public.ml_forecasts FOR DELETE
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = ml_forecasts.business_id AND bm.user_id = auth.uid() AND bm.role = 'owner'));

-- AI Insights
DROP POLICY IF EXISTS "Members can read insights of their businesses" ON public.ai_insights;
CREATE POLICY "Members can read insights of their businesses" ON public.ai_insights FOR SELECT
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = ai_insights.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Members can insert insights for their businesses" ON public.ai_insights;
CREATE POLICY "Members can insert insights for their businesses" ON public.ai_insights FOR INSERT
    WITH CHECK (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = ai_insights.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Members can update insights for their businesses" ON public.ai_insights;
CREATE POLICY "Members can update insights for their businesses" ON public.ai_insights FOR UPDATE
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = ai_insights.business_id AND bm.user_id = auth.uid()))
    WITH CHECK (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = ai_insights.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Owners can delete insights" ON public.ai_insights;
CREATE POLICY "Owners can delete insights" ON public.ai_insights FOR DELETE
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = ai_insights.business_id AND bm.user_id = auth.uid() AND bm.role = 'owner'));

-- Copilot Messages
DROP POLICY IF EXISTS "Members can read chat messages for their businesses" ON public.copilot_messages;
CREATE POLICY "Members can read chat messages for their businesses" ON public.copilot_messages FOR SELECT
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = copilot_messages.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Members can insert chat messages for their businesses" ON public.copilot_messages;
CREATE POLICY "Members can insert chat messages for their businesses" ON public.copilot_messages FOR INSERT
    WITH CHECK (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = copilot_messages.business_id AND bm.user_id = auth.uid()));

-- Action Items
DROP POLICY IF EXISTS "Members can read action items of their businesses" ON public.action_items;
CREATE POLICY "Members can read action items of their businesses" ON public.action_items FOR SELECT
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = action_items.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Members can insert action items for their businesses" ON public.action_items;
CREATE POLICY "Members can insert action items for their businesses" ON public.action_items FOR INSERT
    WITH CHECK (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = action_items.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Members can update action items for their businesses" ON public.action_items;
CREATE POLICY "Members can update action items for their businesses" ON public.action_items FOR UPDATE
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = action_items.business_id AND bm.user_id = auth.uid()))
    WITH CHECK (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = action_items.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Owners can delete action items" ON public.action_items;
CREATE POLICY "Owners can delete action items" ON public.action_items FOR DELETE
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = action_items.business_id AND bm.user_id = auth.uid() AND bm.role = 'owner'));

-- Scheduled Reports
DROP POLICY IF EXISTS "Members can read scheduled reports of their businesses" ON public.scheduled_reports;
CREATE POLICY "Members can read scheduled reports of their businesses" ON public.scheduled_reports FOR SELECT
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = scheduled_reports.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Members can insert scheduled reports for their businesses" ON public.scheduled_reports;
CREATE POLICY "Members can insert scheduled reports for their businesses" ON public.scheduled_reports FOR INSERT
    WITH CHECK (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = scheduled_reports.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Members can update scheduled reports for their businesses" ON public.scheduled_reports;
CREATE POLICY "Members can update scheduled reports for their businesses" ON public.scheduled_reports FOR UPDATE
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = scheduled_reports.business_id AND bm.user_id = auth.uid()))
    WITH CHECK (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = scheduled_reports.business_id AND bm.user_id = auth.uid()));

DROP POLICY IF EXISTS "Owners can delete scheduled reports" ON public.scheduled_reports;
CREATE POLICY "Owners can delete scheduled reports" ON public.scheduled_reports FOR DELETE
    USING (EXISTS (SELECT 1 FROM public.business_memberships bm WHERE bm.business_id = scheduled_reports.business_id AND bm.user_id = auth.uid() AND bm.role = 'owner'));
