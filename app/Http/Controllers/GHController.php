<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\GoodHistories;
use App\Models\Tags;
use Inertia\Inertia;

class GHController extends Controller
{
    public function index(Request $request)
    {
        // Get first history to show initially
        $currentHistory = GoodHistories::with(['user', 'tags'])
            ->where('is_moderated', true)
            ->first();
            
        $allTags = Tags::all();

        return Inertia::render('GHShow', [
            'currentHistory' => $currentHistory,
            'allTags' => $allTags,
            'totalHistories' => GoodHistories::where('is_moderated', true)->count(),
        ]);
    }

    public function show($id)
    {
        $history = GoodHistories::with(['user', 'tags'])
            ->where('is_moderated', true)
            ->findOrFail($id);

        return response()->json($history);
    }

    public function getRandomHistory()
    {
        $history = GoodHistories::with(['user', 'tags'])
            ->where('is_moderated', true)
            ->inRandomOrder()
            ->first();

        return response()->json($history);
    }
}