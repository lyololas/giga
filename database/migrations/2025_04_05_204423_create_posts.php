<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{

    public function up(): void
    {
        Schema::create('posts', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->boolean('is_moderated')->default(0);
            $table->string('image')->nullable()->after('description');
            $table->integer('likes')->default(0);
            $table->string('title');
            $table->longText('description');
            $table->timestamps();
        });
    }


    public function down(): void
    {
        Schema::dropIfExists('posts');
    }
};
