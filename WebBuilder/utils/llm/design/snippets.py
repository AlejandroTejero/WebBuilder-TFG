SNIPPETS = {
    "neo_terminal": {
        "card": """<article class="bg-[#050505] border border-[#1f1f1f] p-4 text-white">
  <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="flex items-start gap-4">
    <img src="{{ CAMPO_IMAGEN }}" alt="{{ CAMPO_TITULO }}" class="h-24 w-24 shrink-0 border border-[#1f1f1f] object-cover" />
    <div class="min-w-0 flex-1">
      <div class="mb-2 flex flex-wrap items-center gap-2">
        <span class="inline-flex items-center border border-[#c8ff00] px-2 py-1 text-[11px] font-medium uppercase tracking-[0.2em] text-[#c8ff00]">{{ CAMPO_CATEGORIA }}</span>
        <span class="text-xs uppercase tracking-[0.2em] text-zinc-500">{{ CAMPO_FECHA }}</span>
      </div>
      <h3 class="mb-2 text-lg font-semibold uppercase tracking-[0.12em] text-[#c8ff00]">{{ CAMPO_TITULO }}</h3>
      <p class="text-sm leading-6 text-zinc-300">{{ CAMPO_EXTRA }}</p>
    </div>
  </a>
</article>""",
        "hero": """<section class="border border-[#1f1f1f] bg-[#050505] p-6 text-white md:p-10">
  <div class="mb-4 flex flex-wrap items-center gap-3">
    <span class="inline-flex items-center border border-[#c8ff00] px-3 py-1 text-xs uppercase tracking-[0.3em] text-[#c8ff00]">{{ CAMPO_CATEGORIA }}</span>
    <span class="text-xs uppercase tracking-[0.3em] text-zinc-500">{{ CAMPO_FECHA }}</span>
  </div>
  <div class="grid gap-6 md:grid-cols-[1.1fr_0.9fr] md:items-center">
    <div>
      <h1 class="mb-4 text-4xl font-bold uppercase tracking-[0.12em] text-[#c8ff00] md:text-6xl">{{ CAMPO_TITULO }}</h1>
      <p class="max-w-2xl text-base leading-7 text-zinc-300">{{ CAMPO_EXTRA }}</p>
    </div>
    <img src="{{ CAMPO_IMAGEN }}" alt="{{ CAMPO_TITULO }}" class="h-72 w-full border border-[#1f1f1f] object-cover" />
  </div>
</section>""",
        "list_row": """<article class="border-t border-[#1f1f1f] bg-[#050505] py-4 text-white">
  <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="flex items-start gap-4">
    <img src="{{ CAMPO_IMAGEN }}" alt="{{ CAMPO_TITULO }}" class="h-20 w-20 shrink-0 border border-[#1f1f1f] object-cover" />
    <div class="min-w-0 flex-1">
      <div class="mb-2 flex flex-wrap items-center gap-2">
        <span class="inline-flex items-center border border-[#c8ff00] px-2 py-0.5 text-[10px] uppercase tracking-[0.25em] text-[#c8ff00]">{{ CAMPO_CATEGORIA }}</span>
        <span class="text-xs uppercase tracking-[0.2em] text-zinc-500">{{ CAMPO_FECHA }}</span>
      </div>
      <h3 class="mb-1 text-base font-semibold uppercase tracking-[0.08em] text-zinc-100">{{ CAMPO_TITULO }}</h3>
      <p class="text-sm leading-6 text-zinc-400">{{ CAMPO_EXTRA }}</p>
    </div>
  </a>
</article>""",
    },
    "bento_pop": {
        "card": """<article class="rounded-3xl bg-[#ff7a59] p-5 text-black shadow-sm">
  <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="grid gap-4">
    <img src="{{ CAMPO_IMAGEN }}" alt="{{ CAMPO_TITULO }}" class="h-48 w-full rounded-2xl bg-white/60 object-cover" />
    <div class="flex flex-wrap items-center justify-between gap-3">
      <span class="inline-flex items-center rounded-full bg-[#7c3aed] px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-white">{{ CAMPO_CATEGORIA }}</span>
      <span class="rounded-full bg-white/70 px-3 py-1 text-xs font-medium">{{ CAMPO_FECHA }}</span>
    </div>
    <h3 class="text-2xl font-black leading-tight">{{ CAMPO_TITULO }}</h3>
    <p class="text-sm leading-6 text-black/80">{{ CAMPO_EXTRA }}</p>
  </a>
</article>""",
        "hero": """<section class="grid gap-4 md:grid-cols-3 md:grid-rows-2">
  <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="rounded-3xl bg-[#00c2ff] p-6 text-black md:col-span-2 md:row-span-2">
    <span class="mb-4 inline-flex rounded-full bg-white/70 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em]">{{ CAMPO_CATEGORIA }}</span>
    <h1 class="mb-4 text-4xl font-black leading-none md:text-6xl">{{ CAMPO_TITULO }}</h1>
    <p class="max-w-2xl text-base leading-7 text-black/80">{{ CAMPO_EXTRA }}</p>
  </a>
  <div class="rounded-3xl bg-[#ffd166] p-4">
    <img src="{{ CAMPO_IMAGEN }}" alt="{{ CAMPO_TITULO }}" class="h-full w-full rounded-2xl object-cover" />
  </div>
  <div class="rounded-3xl bg-[#7c3aed] p-6 text-white">
    <p class="text-sm uppercase tracking-[0.2em]">{{ CAMPO_FECHA }}</p>
  </div>
</section>""",
        "list_row": """<article class="rounded-3xl bg-[#fafaf9] p-3">
  <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="grid gap-3 rounded-[1.5rem] bg-[#34d399] p-4 md:grid-cols-[96px_1fr_auto] md:items-center">
    <img src="{{ CAMPO_IMAGEN }}" alt="{{ CAMPO_TITULO }}" class="h-24 w-24 rounded-2xl bg-white/70 object-cover" />
    <div>
      <div class="mb-2 flex flex-wrap items-center gap-2">
        <span class="inline-flex rounded-full bg-[#ff4d8d] px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-white">{{ CAMPO_CATEGORIA }}</span>
        <span class="inline-flex rounded-full bg-white/70 px-3 py-1 text-xs">{{ CAMPO_FECHA }}</span>
      </div>
      <h3 class="text-xl font-black leading-tight text-black">{{ CAMPO_TITULO }}</h3>
    </div>
    <span class="justify-self-start rounded-full bg-[#111827] px-3 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-white md:justify-self-end">Ver</span>
  </a>
</article>""",
    },
    "brutalist_poster": {
        "card": """<article class="rounded-none border-2 border-black bg-[#f5e71c] p-5 text-black">
  <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="block">
    <img src="{{ CAMPO_IMAGEN }}" alt="{{ CAMPO_TITULO }}" class="mb-4 h-48 w-full rounded-none border-2 border-black object-cover" />
    <div class="mb-3 flex flex-wrap items-center gap-2">
      <span class="inline-flex items-center border-2 border-black px-2 py-1 text-xs font-black uppercase tracking-[0.2em]">{{ CAMPO_CATEGORIA }}</span>
      <span class="inline-flex items-center border-2 border-black px-2 py-1 text-xs font-bold uppercase">{{ CAMPO_FECHA }}</span>
    </div>
    <h3 class="mb-3 text-3xl font-black uppercase leading-none">{{ CAMPO_TITULO }}</h3>
    <p class="text-sm font-bold uppercase leading-6">{{ CAMPO_EXTRA }}</p>
  </a>
</article>""",
        "hero": """<section class="rounded-none border-2 border-black bg-[#f5e71c] p-6 text-black md:p-10">
  <div class="grid gap-6 md:grid-cols-[0.9fr_1.1fr] md:items-stretch">
    <div class="border-2 border-black p-4">
      <p class="mb-3 text-xs font-black uppercase tracking-[0.3em]">{{ CAMPO_CATEGORIA }}</p>
      <h1 class="text-5xl font-black uppercase leading-none md:text-7xl">{{ CAMPO_TITULO }}</h1>
    </div>
    <img src="{{ CAMPO_IMAGEN }}" alt="{{ CAMPO_TITULO }}" class="h-72 w-full rounded-none border-2 border-black object-cover md:h-full" />
  </div>
  <div class="mt-6 border-2 border-black p-4">
    <p class="text-sm font-bold uppercase leading-6">{{ CAMPO_EXTRA }}</p>
  </div>
</section>""",
        "list_row": """<article class="border-t-2 border-black bg-[#f5e71c] py-4 text-black">
  <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="grid gap-4 md:grid-cols-[120px_1fr_auto] md:items-center">
    <img src="{{ CAMPO_IMAGEN }}" alt="{{ CAMPO_TITULO }}" class="h-24 w-full rounded-none border-2 border-black object-cover md:w-[120px]" />
    <div>
      <div class="mb-2 flex flex-wrap items-center gap-2">
        <span class="border-2 border-black px-2 py-1 text-[11px] font-black uppercase tracking-[0.2em]">{{ CAMPO_CATEGORIA }}</span>
        <span class="border-2 border-black px-2 py-1 text-[11px] font-bold uppercase">{{ CAMPO_FECHA }}</span>
      </div>
      <h3 class="text-2xl font-black uppercase leading-none">{{ CAMPO_TITULO }}</h3>
    </div>
    <span class="justify-self-start border-2 border-black px-3 py-2 text-xs font-black uppercase tracking-[0.2em] md:justify-self-end">Ver</span>
  </a>
</article>""",
    },
    "magazine_split": {
        "card": """<article class="border border-[#d8d0c4] bg-[#f7f3eb] p-4 text-[#1f1f1f]">
  <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="grid gap-4 md:grid-cols-[1.1fr_0.9fr] md:items-start">
    <img src="{{ CAMPO_IMAGEN }}" alt="{{ CAMPO_TITULO }}" class="h-64 w-full object-cover" />
    <div>
      <p class="mb-3 text-[11px] uppercase tracking-[0.3em] text-[#7a6f61]">{{ CAMPO_CATEGORIA }} · {{ CAMPO_FECHA }}</p>
      <h3 class="mb-3 font-serif text-3xl leading-tight text-[#1f1f1f]">{{ CAMPO_TITULO }}</h3>
      <div class="mb-4 h-px w-full bg-[#d8d0c4]"></div>
      <p class="text-sm leading-7 text-[#4b463f]">{{ CAMPO_EXTRA }}</p>
    </div>
  </a>
</article>""",
        "hero": """<section class="border-y border-[#d8d0c4] bg-[#f7f3eb] py-8 text-[#1f1f1f]">
  <div class="grid gap-8 md:grid-cols-[1.15fr_0.85fr] md:items-stretch">
    <img src="{{ CAMPO_IMAGEN }}" alt="{{ CAMPO_TITULO }}" class="h-[28rem] w-full object-cover" />
    <div class="flex flex-col justify-center">
      <p class="mb-4 text-[11px] uppercase tracking-[0.35em] text-[#7a6f61]">{{ CAMPO_CATEGORIA }}</p>
      <h1 class="mb-5 font-serif text-5xl leading-tight md:text-6xl">{{ CAMPO_TITULO }}</h1>
      <div class="mb-5 h-px w-24 bg-[#b8afa2]"></div>
      <p class="text-base leading-8 text-[#4b463f]">{{ CAMPO_EXTRA }}</p>
    </div>
  </div>
</section>""",
        "list_row": """<article class="border-t border-[#d8d0c4] bg-[#f7f3eb] py-5 text-[#1f1f1f]">
  <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="grid gap-5 md:grid-cols-[220px_1fr] md:items-start">
    <img src="{{ CAMPO_IMAGEN }}" alt="{{ CAMPO_TITULO }}" class="h-36 w-full object-cover" />
    <div>
      <p class="mb-2 text-[11px] uppercase tracking-[0.3em] text-[#7a6f61]">{{ CAMPO_CATEGORIA }} · {{ CAMPO_FECHA }}</p>
      <h3 class="mb-3 font-serif text-2xl leading-snug">{{ CAMPO_TITULO }}</h3>
      <p class="text-sm leading-7 text-[#4b463f]">{{ CAMPO_EXTRA }}</p>
    </div>
  </a>
</article>""",
    },
    "glass_orbit": {
        "card": """<article class="rounded-3xl border border-white/40 bg-white/40 p-5 shadow-lg backdrop-blur-xl">
  <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="grid gap-4">
    <img src="{{ CAMPO_IMAGEN }}" alt="{{ CAMPO_TITULO }}" class="h-48 w-full rounded-2xl object-cover" />
    <div class="flex flex-wrap items-center justify-between gap-3">
      <span class="inline-flex items-center rounded-full border border-white/50 bg-white/30 px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] text-slate-700">{{ CAMPO_CATEGORIA }}</span>
      <span class="inline-flex items-center rounded-full bg-white/30 px-3 py-1 text-xs text-slate-600">{{ CAMPO_FECHA }}</span>
    </div>
    <h3 class="text-2xl font-semibold leading-tight text-slate-900">{{ CAMPO_TITULO }}</h3>
    <p class="text-sm leading-7 text-slate-700">{{ CAMPO_EXTRA }}</p>
  </a>
</article>""",
        "hero": """<section class="rounded-[2rem] border border-white/40 bg-gradient-to-br from-indigo-500/30 via-violet-400/20 to-white/20 p-6 shadow-lg backdrop-blur-xl md:p-10">
  <div class="grid gap-6 md:grid-cols-[1.05fr_0.95fr] md:items-center">
    <div>
      <span class="mb-4 inline-flex rounded-full border border-white/50 bg-white/30 px-3 py-1 text-xs uppercase tracking-[0.25em] text-slate-700">{{ CAMPO_CATEGORIA }}</span>
      <h1 class="mb-4 text-4xl font-semibold leading-tight text-slate-900 md:text-6xl">{{ CAMPO_TITULO }}</h1>
      <p class="max-w-2xl text-base leading-8 text-slate-700">{{ CAMPO_EXTRA }}</p>
    </div>
    <img src="{{ CAMPO_IMAGEN }}" alt="{{ CAMPO_TITULO }}" class="h-80 w-full rounded-[1.5rem] object-cover ring-1 ring-white/50" />
  </div>
</section>""",
        "list_row": """<article class="rounded-3xl border border-white/40 bg-white/35 p-3 shadow-sm backdrop-blur-xl">
  <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="grid gap-4 rounded-[1.5rem] p-3 md:grid-cols-[96px_1fr_auto] md:items-center">
    <img src="{{ CAMPO_IMAGEN }}" alt="{{ CAMPO_TITULO }}" class="h-24 w-24 rounded-2xl object-cover ring-1 ring-white/50" />
    <div>
      <div class="mb-2 flex flex-wrap items-center gap-2">
        <span class="rounded-full border border-white/50 bg-white/30 px-3 py-1 text-xs uppercase tracking-[0.2em] text-slate-700">{{ CAMPO_CATEGORIA }}</span>
        <span class="rounded-full bg-white/30 px-3 py-1 text-xs text-slate-600">{{ CAMPO_FECHA }}</span>
      </div>
      <h3 class="text-xl font-semibold leading-tight text-slate-900">{{ CAMPO_TITULO }}</h3>
    </div>
    <span class="justify-self-start rounded-full border border-white/50 bg-white/30 px-3 py-2 text-xs uppercase tracking-[0.2em] text-slate-700 md:justify-self-end">Ver</span>
  </a>
</article>""",
    },
    "quiet_editorial": {
        "card": """<article class="border-b border-[#ece7df] bg-[#fffdf8] py-8 text-[#1f1b16]">
  <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="block max-w-2xl">
    <div class="mb-3 flex flex-wrap items-center gap-3">
      <span class="text-[11px] uppercase tracking-[0.3em] text-[#8b8175]">{{ CAMPO_CATEGORIA }}</span>
      <span class="text-[11px] uppercase tracking-[0.3em] text-[#b0a79b]">{{ CAMPO_FECHA }}</span>
    </div>
    <h3 class="mb-4 font-serif text-3xl leading-tight">{{ CAMPO_TITULO }}</h3>
    <p class="mb-4 text-base leading-8 text-[#4e473f]">{{ CAMPO_EXTRA }}</p>
    <span class="text-xs uppercase tracking-[0.25em] text-[#8b8175]">{{ CAMPO_EXTRA }}</span>
  </a>
</article>""",
        "hero": """<section class="bg-[#fffdf8] py-16 text-[#1f1b16]">
  <div class="mx-auto max-w-3xl">
    <p class="mb-4 text-[11px] uppercase tracking-[0.35em] text-[#8b8175]">{{ CAMPO_CATEGORIA }}</p>
    <h1 class="mb-6 font-serif text-5xl leading-tight md:text-6xl">{{ CAMPO_TITULO }}</h1>
    <div class="mb-6 h-px w-16 bg-[#d9d1c6]"></div>
    <p class="mb-6 text-lg leading-9 text-[#4e473f]">{{ CAMPO_EXTRA }}</p>
    <p class="text-sm leading-8 text-[#8b8175]">{{ CAMPO_FECHA }}</p>
  </div>
</section>""",
        "list_row": """<article class="border-b border-[#ece7df] bg-[#fffdf8] py-6 text-[#1f1b16]">
  <a href="{% url 'NOMBRE_URL_DETALLE' item.pk %}" class="mx-auto block max-w-3xl">
    <div class="mb-2 flex flex-wrap items-center gap-3">
      <span class="text-[11px] uppercase tracking-[0.3em] text-[#8b8175]">{{ CAMPO_CATEGORIA }}</span>
      <span class="text-[11px] uppercase tracking-[0.3em] text-[#b0a79b]">{{ CAMPO_FECHA }}</span>
    </div>
    <h3 class="mb-3 font-serif text-2xl leading-snug">{{ CAMPO_TITULO }}</h3>
    <p class="mb-2 text-sm leading-8 text-[#4e473f]">{{ CAMPO_EXTRA }}</p>
    <span class="text-[11px] uppercase tracking-[0.3em] text-[#b0a79b]">{{ CAMPO_EXTRA }}</span>
  </a>
</article>""",
    },
}


def get_snippet(preset_id: str, kind: str) -> str:
    """kind puede ser 'card', 'hero' o 'list_row'. Devuelve '' si no existe."""
    return SNIPPETS.get(preset_id, {}).get(kind, "")