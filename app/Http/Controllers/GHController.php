<?php

namespace App\Http\Controllers;

use Inertia\Inertia;
use App\Models\GoodHistories;
use App\Models\Tags;

class GHController extends Controller
{
    public function index()
    {
        $currentHistory = GoodHistories::with(['user', 'tags'])
            ->where('is_moderated', true)
            ->first();

        $author = $currentHistory ? $currentHistory->user->name ?? $currentHistory->user->id : null;

        $allTags = Tags::all();
        $totalHistories = GoodHistories::where('is_moderated', true)->count();

        return Inertia::render('GHShow', [
            'currentHistory' => $currentHistory,
            'author' => $author, 
            'allTags' => $allTags,
            'totalHistories' => $totalHistories,
        ]);
    }

    public function random()
    {
        $history = GoodHistories::with(['user', 'tags'])
            ->where('is_moderated', true)
            ->inRandomOrder()
            ->first();

        return Inertia::render('GHShow', [
            'currentHistory' => $history,
            'allTags' => Tags::all(),
            'totalHistories' => GoodHistories::where('is_moderated', true)->count(),
        ]);
    }
}