<?php

use Illuminate\Support\Facades\Route;
use Inertia\Inertia;
use App\Http\Controllers\PostsController;
use App\Http\Controllers\GHController;
Route::get('/', function () {
    return Inertia::render('Welcome');
})->name('home');

Route::get('dashboard', function () {
    return Inertia::render('Dashboard');
})->middleware(['auth', 'verified'])->name('dashboard');

Route::get('gh', function () {
    return Inertia::render('GHShow');
})->name('gh.show');

Route::get('/forum', [PostsController::class, 'index'])->name('forum.index');
Route::middleware('auth')->group(function () {
    Route::get('/forum/{id}', [PostsController::class, 'show'])->name('post.show');
    Route::post('/forum/{post}/comments', [PostsController::class, 'storeComment'])->name('posts.comment.store');
    Route::post('/forum', [PostsController::class, 'store'])->name('posts.store');
});
require __DIR__.'/settings.php';
require __DIR__.'/auth.php';
