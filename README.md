# Tailspin Toys

This repository contains the project for a 1 hour guided workshop to explore GitHub Copilot Agent Mode and related features in Visual Studio Code. The project is a website for a fictional game crowd-funding company, with a [Flask](https://flask.palletsprojects.com/en/stable/) backend using [SQLAlchemy](https://www.sqlalchemy.org/) and [Astro](https://astro.build/) frontend using [Svelte](https://svelte.dev/) for dynamic pages.

## Features

### Game Filtering

Users can filter the game catalog by:

- **Category**: Filter games by their category (e.g., Strategy, Card Game, Puzzle)
- **Publisher**: Filter games by their publisher
- **Combined Filters**: Use both category and publisher filters together for more specific results
- **Clear Filters**: Easily reset all filters to view the complete catalog

The filtering functionality is available on the main games page and updates dynamically without page reloads.

### Game Pagination & Sorting

The games list now supports efficient browsing for larger catalogs:

- **Pagination Controls**: Navigate between pages, change page size (10, 20, or 50 games per page), and view the total number of available games.
- **URL Parameters**: The API supports `page`, `per_page`, `sort`, and `order` parameters for consistent pagination and sorting behavior.
- **Sorting Options**: Sort games by title, star rating, or date added (ID) in ascending or descending order.
- **Filter Integration**: Pagination state resets when filters change to make sure results stay in sync with your selections.

## Start the workshop

**To begin the workshop, start at [docs/README.md](./docs/README.md)**

Or, if just want to run the app...

## Launch the site

A script file has been created to launch the site. You can run it by:

```bash
./scripts/start-app.sh
```

Then navigate to the [website](http://localhost:4321) to see the site!

## License

This project is licensed under the terms of the MIT open source license. Please refer to the [LICENSE](./LICENSE) for the full terms.

## Maintainers

You can find the list of maintainers in [CODEOWNERS](./.github/CODEOWNERS).

## Support

This project is provided as-is, and may be updated over time. If you have questions, please open an issue.
