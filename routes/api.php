<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Models\User;
use Illuminate\Support\Facades\Hash;

// Add this route in routes/api.php (not web.php)
Route::post('/telegram/register', function (Request $request) {
    // Verify the bot token
    if ($request->header('X-Telegram-Bot-Token') !== env('TELEGRAM_API_SECRET')) {
        return response()->json(['message' => 'Unauthorized'], 401);
    }

    try {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'email' => 'required|email|unique:users',
            'password' => 'required|string|min:8',
            'telegram_chat_id' => 'required|integer|unique:users,telegram_chat_id'
        ]);

        $user = User::create([
            'name' => $validated['name'],
            'email' => $validated['email'],
            'password' => Hash::make($validated['password']),
            'telegram_chat_id' => $validated['telegram_chat_id'],
        ]);

        return response()->json([
            'message' => 'User registered successfully',
            'user_id' => $user->id
        ], 201);

    } catch (\Exception $e) {
        return response()->json([
            'message' => 'Registration failed',
            'error' => $e->getMessage()
        ], 400);
    }
})->withoutMiddleware(['csrf']); // This disables CSRF protection for this route