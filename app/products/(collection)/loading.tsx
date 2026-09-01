import Container from "@/components/Container";

export default function ProductsLoading() {
  return (
    <main className="min-h-screen bg-background pb-12 pt-24" aria-busy="true" aria-label="Loading products">
      <Container>
        <div className="h-12 w-72 animate-pulse rounded bg-muted motion-reduce:animate-none" />
        <div className="mt-10 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 8 }, (_, index) => (
            <div key={index} className="overflow-hidden rounded-lg border bg-card">
              <div className="aspect-[4/5] animate-pulse bg-muted motion-reduce:animate-none" />
              <div className="space-y-3 p-5">
                <div className="h-3 w-24 animate-pulse rounded bg-muted motion-reduce:animate-none" />
                <div className="h-6 w-3/4 animate-pulse rounded bg-muted motion-reduce:animate-none" />
                <div className="h-4 w-full animate-pulse rounded bg-muted motion-reduce:animate-none" />
              </div>
            </div>
          ))}
        </div>
      </Container>
    </main>
  );
}
