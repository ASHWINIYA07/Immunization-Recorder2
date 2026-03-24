-- =============================================================
-- AI Immunization Recorder — Notification System Schema
-- =============================================================

-- Enum for vaccination status
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'vaccine_status') THEN
        CREATE TYPE vaccine_status AS ENUM ('done', 'upcoming', 'overdue');
    END IF;
END $$;

-- Enum for priority
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'reminder_priority') THEN
        CREATE TYPE reminder_priority AS ENUM ('normal', 'urgent');
    END IF;
END $$;

-- =============================================================
-- 1. children
-- =============================================================
CREATE TABLE IF NOT EXISTS children (
    id           SERIAL PRIMARY KEY,
    name         TEXT        NOT NULL,
    dob          DATE        NOT NULL,
    phone_number TEXT,
    email        TEXT,
    device_token TEXT,
    created_at   TIMESTAMP   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_children_name ON children (name);

-- =============================================================
-- 2. vaccines
-- =============================================================
CREATE TABLE IF NOT EXISTS vaccines (
    id       SERIAL PRIMARY KEY,
    name     TEXT    NOT NULL UNIQUE,
    due_days INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_vaccines_name ON vaccines (name);

-- =============================================================
-- 3. vaccination_records
-- =============================================================
CREATE TABLE IF NOT EXISTS vaccination_records (
    id         SERIAL PRIMARY KEY,
    child_id   INTEGER       NOT NULL REFERENCES children (id) ON DELETE CASCADE,
    vaccine_id INTEGER       NOT NULL REFERENCES vaccines (id) ON DELETE CASCADE,
    status     vaccine_status NOT NULL DEFAULT 'upcoming',
    taken_date DATE,
    created_at TIMESTAMP     NOT NULL DEFAULT NOW(),
    UNIQUE (child_id, vaccine_id)
);

CREATE INDEX IF NOT EXISTS idx_vrecords_child  ON vaccination_records (child_id);
CREATE INDEX IF NOT EXISTS idx_vrecords_status ON vaccination_records (status);

-- =============================================================
-- 4. reminders
-- =============================================================
CREATE TABLE IF NOT EXISTS reminders (
    id            SERIAL PRIMARY KEY,
    child_id      INTEGER          NOT NULL REFERENCES children (id) ON DELETE CASCADE,
    vaccine_id    INTEGER          NOT NULL REFERENCES vaccines (id) ON DELETE CASCADE,
    reminder_type TEXT             NOT NULL,   -- 7_day | 2_day | due_today | overdue_3 | overdue_7
    reminder_date TIMESTAMP        NOT NULL,
    sent_status   BOOLEAN          NOT NULL DEFAULT FALSE,
    channel       TEXT             NOT NULL,   -- sms | whatsapp | email | push
    priority      reminder_priority NOT NULL DEFAULT 'normal',
    queued        BOOLEAN          NOT NULL DEFAULT FALSE,
    last_sent_at  TIMESTAMP,
    -- Prevent duplicate reminders for the same child/vaccine/type/channel
    UNIQUE (child_id, vaccine_id, reminder_type, channel)
);

CREATE INDEX IF NOT EXISTS idx_reminders_child        ON reminders (child_id);
CREATE INDEX IF NOT EXISTS idx_reminders_sent         ON reminders (sent_status);
CREATE INDEX IF NOT EXISTS idx_reminders_queued       ON reminders (queued);
CREATE INDEX IF NOT EXISTS idx_reminders_reminder_date ON reminders (reminder_date);
