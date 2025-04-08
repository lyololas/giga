<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

class EnablePostgisExtension extends Migration
{
    public function up()
    {
        DB::statement('CREATE EXTENSION IF NOT EXISTS postgis');
    }

    public function down()
    {
        // Drop the volunteers table if it exists
        Schema::dropIfExists('volunteers');

        // Now drop the PostGIS extension
        DB::statement('DROP EXTENSION IF EXISTS postgis');
    }
}
