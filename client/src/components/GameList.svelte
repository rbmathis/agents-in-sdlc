<script lang="ts">
    import { onMount } from "svelte";

    interface GameApiPublisher {
        id: number;
        name: string;
    }

    interface GameApiCategory {
        id: number;
        name: string;
    }

    interface GameApiResponse {
        id: number;
        title: string;
        description: string;
        publisher?: GameApiPublisher | null;
        category?: GameApiCategory | null;
        starRating?: number | null;
    }

    interface Game {
        id: number;
        title: string;
        description: string;
        publisher_name?: string;
        category_name?: string;
        starRating?: number | null;
    }

    interface Publisher {
        id: number;
        name: string;
    }

    interface Category {
        id: number;
        name: string;
    }

    interface Pagination {
        page: number;
        per_page: number;
        total_items: number;
        total_pages: number;
        has_next: boolean;
        has_previous: boolean;
    }

    export let games: Game[] = [];
    let loading = true;
    let error: string | null = null;
    let publishers: Publisher[] = [];
    let categories: Category[] = [];
    let selectedPublisherId: string = '';
    let selectedCategoryId: string = '';
    let pagination: Pagination = {
        page: 1,
        per_page: 20,
        total_items: 0,
        total_pages: 1,
        has_next: false,
        has_previous: false,
    };
    let currentPage: number = 1;
    let pageSize: number = 20;
    const pageSizeOptions: number[] = [10, 20, 50];

    $: totalItems = pagination.total_items;
    $: showingStart = totalItems === 0 ? 0 : (pagination.page - 1) * pagination.per_page + 1;
    $: showingEnd = totalItems === 0 ? 0 : Math.min(pagination.page * pagination.per_page, totalItems);
    /**
     * Smart pagination: returns an array of page numbers and ellipsis for display.
     * Always shows first, last, current, and up to 2 pages before/after current.
     */
    $: paginationItems = (() => {
        const total = pagination.total_pages;
        const current = pagination.page;
        const windowSize = 2; // pages before/after current
        if (total <= 7) {
            // Show all if few pages
            return Array.from({ length: total }, (_, i) => i + 1);
        }
        const items: (number | string)[] = [];
        items.push(1);
        if (current > windowSize + 2) {
            items.push('...');
        }
        for (let i = Math.max(2, current - windowSize); i <= Math.min(total - 1, current + windowSize); i++) {
            items.push(i);
        }
        if (current < total - windowSize - 1) {
            items.push('...');
        }
        items.push(total);
        return items;
    })();

    const syncFiltersFromUrl = (): void => {
        if (typeof window === 'undefined') {
            return;
        }

        const params = new URLSearchParams(window.location.search);
        const urlCategoryId = params.get('category_id') ?? '';
        const urlPublisherId = params.get('publisher_id') ?? '';
        const urlPage = params.get('page');
        const urlPerPage = params.get('per_page');

        selectedCategoryId = urlCategoryId;
        selectedPublisherId = urlPublisherId;

        const parsedPage = urlPage ? Number.parseInt(urlPage, 10) : 1;
        currentPage = Number.isNaN(parsedPage) || parsedPage < 1 ? 1 : parsedPage;

        if (urlPerPage) {
            const parsedPerPage = Number.parseInt(urlPerPage, 10);
            if (!Number.isNaN(parsedPerPage) && pageSizeOptions.includes(parsedPerPage)) {
                pageSize = parsedPerPage;
            }
        }
    };

    const updateBrowserUrl = (paginationState: Pagination): void => {
        if (typeof window === 'undefined') {
            return;
        }

        const params = new URLSearchParams();

        if (selectedCategoryId) {
            params.set('category_id', selectedCategoryId);
        }

        if (selectedPublisherId) {
            params.set('publisher_id', selectedPublisherId);
        }

        params.set('page', paginationState.page.toString());
        params.set('per_page', paginationState.per_page.toString());

        const queryString = params.toString();
        const newUrl = `${window.location.pathname}${queryString ? `?${queryString}` : ''}`;
        window.history.replaceState({}, '', newUrl);
    };

    /**
     * Fetches all games from the API endpoint.
     * Updates the games array on success or sets error state on failure.
     */
    const fetchGames = async () => {
        loading = true;
        try {
            const params = new URLSearchParams();
            if (selectedPublisherId) {
                params.append('publisher_id', selectedPublisherId);
            }
            if (selectedCategoryId) {
                params.append('category_id', selectedCategoryId);
            }
            params.append('page', currentPage.toString());
            params.append('per_page', pageSize.toString());
            
            const url = `/api/games${params.toString() ? '?' + params.toString() : ''}`;
            const response = await fetch(url);
            if(response.ok) {
                const payload = await response.json();
                const apiGames: GameApiResponse[] = payload?.games ?? [];
                const apiPagination: Pagination = payload?.pagination ?? pagination;

                games = apiGames.map((game) => ({
                    id: game.id,
                    title: game.title,
                    description: game.description,
                    publisher_name: game.publisher?.name,
                    category_name: game.category?.name,
                    starRating: game.starRating ?? null,
                }));

                pagination = apiPagination;
                currentPage = pagination.page;
                pageSize = pagination.per_page;

                updateBrowserUrl(pagination);
            } else {
                error = `Failed to fetch data: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };

    const fetchPublishers = async () => {
        try {
            const response = await fetch('/api/publishers');
            if (response.ok) {
                publishers = await response.json();
            }
        } catch (err) {
            console.error('Failed to fetch publishers:', err);
        }
    };

    const fetchCategories = async () => {
        try {
            const response = await fetch('/api/categories');
            if (response.ok) {
                categories = await response.json();
            }
        } catch (err) {
            console.error('Failed to fetch categories:', err);
        }
    };

    const handleFilterChange = () => {
        currentPage = 1;
        fetchGames();
    };

    const clearFilters = () => {
        selectedPublisherId = '';
        selectedCategoryId = '';
        currentPage = 1;
        fetchGames();
    };

    const changePage = (page: number) => {
        if (page !== currentPage && page >= 1 && page <= pagination.total_pages) {
            currentPage = page;
            fetchGames();
        }
    };

    const changePageSize = (size: number) => {
        pageSize = size;
        currentPage = 1;
        fetchGames();
    };

    onMount(() => {
        syncFiltersFromUrl();
        fetchPublishers();
        fetchCategories();
        fetchGames();
    });
</script>

<div>
    <div class="flex justify-between items-start mb-6">
        <h2 class="text-2xl font-medium text-slate-100">Featured Games</h2>
        
        <!-- Filter controls -->
        <div class="flex gap-3 items-center">
            <div class="flex gap-2">
                <select 
                    bind:value={selectedCategoryId}
                    on:change={handleFilterChange}
                    class="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 px-3 py-2 cursor-pointer"
                    data-testid="category-filter"
                >
                    <option value="">All Categories</option>
                    {#each categories as category}
                        <option value={category.id}>{category.name}</option>
                    {/each}
                </select>

                <select 
                    bind:value={selectedPublisherId}
                    on:change={handleFilterChange}
                    class="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 px-3 py-2 cursor-pointer"
                    data-testid="publisher-filter"
                >
                    <option value="">All Publishers</option>
                    {#each publishers as publisher}
                        <option value={publisher.id}>{publisher.name}</option>
                    {/each}
                </select>
            </div>

            {#if selectedCategoryId || selectedPublisherId}
                <button 
                    on:click={clearFilters}
                    class="text-sm text-blue-400 hover:text-blue-300 underline transition-colors"
                    data-testid="clear-filters"
                >
                    Clear Filters
                </button>
            {/if}
        </div>
    </div>
    
    {#if loading}
        <!-- loading animation -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each Array(6) as _, i}
                <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden shadow-lg border border-slate-700/50">
                    <div class="p-6">
                        <div class="animate-pulse">
                            <div class="h-6 bg-slate-700 rounded w-3/4 mb-3"></div>
                            <div class="h-4 bg-slate-700 rounded w-1/2 mb-4"></div>
                            <div class="h-3 bg-slate-700 rounded w-full mb-3"></div>
                            <div class="h-3 bg-slate-700 rounded w-5/6 mb-4"></div>
                            <div class="h-2 bg-slate-700 rounded-full w-full mb-2"></div>
                            <div class="h-4 bg-slate-700 rounded w-1/4 mt-4"></div>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {:else if error}
        <!-- error display -->
        <div class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700">
            <p class="text-red-400">{error}</p>
        </div>
    {:else if games.length === 0}
        <!-- no games found -->
        <div class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700">
            <p class="text-slate-300">No games available at the moment.</p>
        </div>
    {:else}
        <!-- game list -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="games-grid">
            {#each games as game (game.id)}
                <a 
                    href={`/game/${game.id}`} 
                    class="group block bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden shadow-lg border border-slate-700/50 hover:border-blue-500/50 hover:shadow-blue-500/10 hover:shadow-xl transition-all duration-300 hover:translate-y-[-6px]"
                    data-testid="game-card"
                    data-game-id={game.id}
                    data-game-title={game.title}
                >
                    <div class="p-6 relative">
                        <div class="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        <div class="relative z-10">
                            <h3 class="text-xl font-semibold text-slate-100 mb-2 group-hover:text-blue-400 transition-colors" data-testid="game-title">{game.title}</h3>
                            
                            {#if game.category_name || game.publisher_name}
                                <div class="flex gap-2 mb-3">
                                    {#if game.category_name}
                                        <span class="text-xs font-medium px-2.5 py-0.5 rounded bg-blue-900/60 text-blue-300" data-testid="game-category">
                                            {game.category_name}
                                        </span>
                                    {/if}
                                    {#if game.publisher_name}
                                        <span class="text-xs font-medium px-2.5 py-0.5 rounded bg-purple-900/60 text-purple-300" data-testid="game-publisher">
                                            {game.publisher_name}
                                        </span>
                                    {/if}
                                </div>
                            {/if}
                            
                            <p class="text-slate-400 mb-4 text-sm line-clamp-2" data-testid="game-description">{game.description}</p>
                            
                            <div class="mt-4 text-sm text-blue-400 font-medium flex items-center">
                                <span>View details</span>
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1 transform transition-transform duration-300 group-hover:translate-x-2" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M12.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                                </svg>
                            </div>
                        </div>
                    </div>
                </a>
            {/each}
        </div>

        <div class="mt-8 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between text-slate-300">
            <div class="text-sm">
                Showing <span class="font-semibold text-slate-100">{showingStart}</span> to <span class="font-semibold text-slate-100">{showingEnd}</span> of <span class="font-semibold text-slate-100">{totalItems}</span> games
            </div>

            <div class="flex flex-col lg:flex-row lg:items-center gap-4">
                <div class="flex items-center gap-2">
                    <label for="page-size" class="text-sm">Games per page:</label>
                    <select
                        id="page-size"
                        bind:value={pageSize}
                        on:change={(event) => changePageSize(Number((event.target as HTMLSelectElement).value))}
                        class="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 px-3 py-2 cursor-pointer"
                        data-testid="page-size-selector"
                    >
                        {#each pageSizeOptions as option}
                            <option value={option}>{option}</option>
                        {/each}
                    </select>
                </div>

                <div class="flex items-center gap-2" data-testid="pagination-controls">
                    <button
                        on:click={() => changePage(pagination.page - 1)}
                        disabled={!pagination.has_previous}
                        class="px-3 py-2 rounded-lg border border-slate-700 bg-slate-800 text-slate-200 text-sm disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-700 transition-colors"
                    >
                        Previous
                    </button>

                    <div class="flex items-center gap-1">
                        {#each pageNumbers as pageNumber}
                            <button
                                class={`w-9 h-9 rounded-lg border text-sm ${pageNumber === pagination.page ? 'border-blue-500 bg-blue-500/20 text-blue-300 font-semibold' : 'border-slate-700 bg-slate-800 text-slate-200 hover:bg-slate-700'}`}
                                on:click={() => changePage(pageNumber)}
                                aria-current={pageNumber === pagination.page ? 'page' : undefined}
                                aria-label={`Page ${pageNumber}`}
                            >
                                {pageNumber}
                            </button>
                        {/each}
                    </div>

                    <button
                        on:click={() => changePage(pagination.page + 1)}
                        disabled={!pagination.has_next}
                        class="px-3 py-2 rounded-lg border border-slate-700 bg-slate-800 text-slate-200 text-sm disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-700 transition-colors"
                    >
                        Next
                    </button>
                </div>
            </div>
        </div>
    {/if}
</div>