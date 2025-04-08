<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

class EnablePgcryptoExtension extends Migration
{
    public function up()
    {
        DB::statement('CREATE EXTENSION IF NOT EXISTS pgcrypto');
    }

    public function down()
    {
        DB::statement('DROP EXTENSION IF EXISTS pgcrypto');
    }
}
