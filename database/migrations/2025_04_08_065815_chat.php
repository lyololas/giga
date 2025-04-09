<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
{
    Schema::create('chats', function (Blueprint $table) {
        $table->id();
        $table->foreignId('user_id')->constrained()->onDelete('cascade');
        $table->foreignId('volunteer_id')->constrained('users')->onDelete('cascade');
        $table->foreignId('help_request_id')->constrained('help_requests')->onDelete('cascade'); // Changed to non-nullable
        $table->string('token', 64)->unique(); 
        $table->timestamp('started_at')->useCurrent();
        $table->timestamp('ended_at')->nullable();
        $table->timestamps();
        
        // Composite index for common queries
        $table->index(['user_id', 'volunteer_id']);
        $table->index(['token', 'ended_at']);
    });
}

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('chats');
    }
};
