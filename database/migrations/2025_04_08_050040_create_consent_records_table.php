<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('consent_records', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained('users')->onDelete('cascade'); // Foreign key reference
            $table->timestamp('consent_given_at');
            $table->string('version');
            $table->timestamps();
        });
    }

    public function down()      
    {
        Schema::dropIfExists('consent_records');
    }
};