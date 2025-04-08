<?php


use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\TelegramAuthController;

Route::post('/telegram/register', [TelegramAuthController::class, 'register']);
    