<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up()
    {
        DB::statement('
            CREATE TABLE help_requests (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                volunteer_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                location GEOGRAPHY(POINT, 4326),
                geofence GEOGRAPHY(POLYGON, 4326),
                requested_at TIMESTAMP NOT NULL DEFAULT NOW(),
                accepted_at TIMESTAMP,
                status VARCHAR(20) NOT NULL DEFAULT \'pending\',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        ');
        
        // Create spatial indexes
        DB::statement('CREATE INDEX idx_help_requests_location ON help_requests USING GIST(location)');
        DB::statement('CREATE INDEX idx_help_requests_geofence ON help_requests USING GIST(geofence)');
    }

    public function down()
    {
        DB::statement('DROP TABLE IF EXISTS help_requests');
    }
};