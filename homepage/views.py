"""Представления главной страницы и общий HTML-каркас."""

from html import escape

from django.http import HttpRequest, HttpResponse

BOOTSTRAP_CSS = (
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/"
    "dist/css/bootstrap.min.css"
)
BOOTSTRAP_JS = (
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/"
    "dist/js/bootstrap.bundle.min.js"
)

NAV_ITEMS = (
    ("/", "Главная", "home"),
    ("/chores/", "Дела", "chores"),
    ("/categories/", "Категории", "categories"),
)


def page(title: str, content: str, active: str = "") -> str:
    """Собрать HTML-страницу с навбаром и Bootstrap 5.3."""
    links = []
    for url, label, key in NAV_ITEMS:
        current = " active" if key == active else ""
        links.append(
            f'<li class="nav-item">'
            f'<a class="nav-link{current}" href="{url}">{label}</a>'
            f"</li>"
        )
    navbar = "".join(links)
    safe_title = escape(title)
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title} — Home Tasks</title>
  <link href="{BOOTSTRAP_CSS}" rel="stylesheet">
</head>
<body class="bg-light">
  <nav class="navbar navbar-expand-lg navbar-dark bg-success">
    <div class="container">
      <a class="navbar-brand" href="/">Home Tasks</a>
      <button class="navbar-toggler" type="button"
              data-bs-toggle="collapse"
              data-bs-target="#navbarNav"
              aria-controls="navbarNav"
              aria-expanded="false"
              aria-label="Меню">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          {navbar}
        </ul>
      </div>
    </div>
  </nav>
  <main class="container py-4">
    <h1 class="mb-4">{safe_title}</h1>
    {content}
  </main>
  <script src="{BOOTSTRAP_JS}"></script>
</body>
</html>
"""


def index(request: HttpRequest) -> HttpResponse:
    """Показать главную страницу сервиса."""
    content = """
    <p class="lead">
      Сервис учета домашних дел: просмотр задач семьи,
      исполнителей, категорий и сроков выполнения.
    </p>
    <div class="row g-3">
      <div class="col-md-6">
        <div class="card h-100">
          <div class="card-body">
            <h2 class="h5 card-title">Дела</h2>
            <p class="card-text">
              Список домашних дел из JSON и карточка каждого дела.
            </p>
            <a class="btn btn-success" href="/chores/">Открыть дела</a>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card h-100">
          <div class="card-body">
            <h2 class="h5 card-title">Категории</h2>
            <p class="card-text">
              Справочник категорий и дела внутри каждой группы.
            </p>
            <a class="btn btn-outline-success" href="/categories/">
              Открыть категории
            </a>
          </div>
        </div>
      </div>
    </div>
    """
    return HttpResponse(page("Главная", content, active="home"))


def page_not_found(request: HttpRequest, exception) -> HttpResponse:
    """Вернуть свою HTML-страницу для неизвестного адреса."""
    content = """
    <p>Запрашиваемая страница не существует.</p>
    <p>
      <a class="btn btn-success" href="/">На главную</a>
    </p>
    """
    return HttpResponse(
        page("Страница не найдена", content),
        status=404,
    )
