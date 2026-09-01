import type { Category, ProductFilters as Filters } from "@/lib/types/api";

export default function ProductFilters({
  categories,
  filters,
}: {
  categories: Category[];
  filters: Filters;
}) {
  const inputClass =
    "h-10 rounded-md border border-input bg-background px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

  return (
    <form action="/products" className="mb-10 grid gap-3 rounded-lg border bg-card p-4 md:grid-cols-5">
      <label className="md:col-span-2">
        <span className="sr-only">Search products</span>
        <input
          className={`${inputClass} w-full`}
          type="search"
          name="search"
          defaultValue={filters.search}
          placeholder="Search the collection"
        />
      </label>
      <label>
        <span className="sr-only">Category</span>
        <select className={`${inputClass} w-full`} name="category" defaultValue={filters.category ?? ""}>
          <option value="">All categories</option>
          {categories.map((category) => (
            <option key={category.slug} value={category.slug}>
              {category.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        <span className="sr-only">Product type</span>
        <select className={`${inputClass} w-full`} name="type" defaultValue={filters.type ?? ""}>
          <option value="">All product types</option>
          <option value="coffee">Coffee</option>
          <option value="equipment">Equipment</option>
          <option value="drinkware">Drinkware</option>
        </select>
      </label>
      <label>
        <span className="sr-only">Sort products</span>
        <select className={`${inputClass} w-full`} name="ordering" defaultValue={filters.ordering ?? "name"}>
          <option value="name">Name: A–Z</option>
          <option value="-name">Name: Z–A</option>
          <option value="price">Price: low to high</option>
          <option value="-price">Price: high to low</option>
        </select>
      </label>
      <div className="flex items-center gap-3 md:col-span-5">
        <label className="flex items-center gap-2 text-sm text-muted-foreground">
          <input
            type="checkbox"
            name="availability"
            value="true"
            defaultChecked={filters.availability === true}
            className="h-4 w-4 rounded border-input accent-primary"
          />
          Available now
        </label>
        <button
          type="submit"
          className="ml-auto h-10 rounded-md bg-primary px-5 text-sm font-medium text-primary-foreground transition-[background-color,transform] duration-150 active:scale-[0.97] motion-reduce:transform-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          Apply filters
        </button>
      </div>
    </form>
  );
}
