<?php

use Illuminate\Support\Facades\Route;
use Inertia\Inertia;
use App\Models\Post;
use App\Models\GoodHistories;
use App\Models\Tags;
use App\Models\Comments;
use App\Models\GoodHistoriesTags;
use App\Http\Controllers\PostsController;
use App\Http\Controllers\GHController;
Route::get('/', function () {
    return Inertia::render('Welcome');
})->name('home');
Route::get('/qrcode', function () {
    return Inertia::render('QrCode');
})->name('qrcode');
Route::get('/dashboard', function () {
    $posts = Post::with(['user'])
                ->where('is_moderated', true)
                ->latest()
                ->take(3)
                ->get();

    $histories = GoodHistories::with(['user'])
                ->where('is_moderated', true)
                ->latest()
                ->take(3)
                ->get();

    $totalPosts = Post::where('is_moderated', true)->count();
    $totalHistories = GoodHistories::where('is_moderated', true)->count();

    return Inertia::render('Dashboard', [
        'posts' => $posts,
        'histories' => $histories,
        'totalPosts' => $totalPosts,
        'totalHistories' => $totalHistories,
    ]);
})->name('dashboard');

Route::get('gh', function () {
    return Inertia::render('GHShow');
})->name('gh.show');
Route::get('gh', [GHController::class, 'index'])->name('gh.index');
Route::get('/gh/{id}', [GHController::class, 'show'])->name('gh.show');

Route::get('/forum', [PostsController::class, 'index'])->name('post.index');
Route::get('/forum/{id}', [PostsController::class, 'show'])->name('post.show');
Route::get('forum/{id}', [PostsController::class, 'show'])->name('post.show');




Route::middleware('auth')->group(function () {
    Route::post('/gh', [PostsController::class, 'store'])->name('gh.store');
    Route::get('/forum/{id}', [PostsController::class, 'show'])->name('forum.show');
    Route::post('/forum/{post}/comments', [PostsController::class, 'storeComment'])->name('forum.comment.store');
    Route::post('/forum', [PostsController::class, 'store'])->name('forum.store');
});
require __DIR__.'/settings.php';
require __DIR__.'/auth.php';
require __DIR__.'/api.php';
