<?php


use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Route;

Route::post('/telegram/register', function (Request $request) {
   
    if ($request->header('X-Telegram-Bot-Token') !== env('TELEGRAM_API_SECRET')) {
        return response()->json(['message' => 'Unauthorized'], 401);
    }

    $validated = $request->validate([
        'name' => 'required|string|max:255',
        'email' => 'required|email|unique:users',
        'password' => 'required|string|min:8',
        'telegram_chat_id' => 'required|integer|unique:users'
    ]);

    $user = User::create([
        'name' => $validated['name'],
        'email' => $validated['email'],
        'password' => Hash::make($validated['password']),
        'telegram_chat_id' => $validated['telegram_chat_id'],
    ]);

    $token = $user->createToken('telegram-token')->plainTextToken;

    return response()->json([
        'message' => 'Registration successful',
        'user_id' => $user->id,
        'access_token' => $token
    ], 201);
});