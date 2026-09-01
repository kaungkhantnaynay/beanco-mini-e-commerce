import ButtonLink from "@/components/ButtonLink";

export function CatalogState({
  title,
  detail,
  retryHref,
}: {
  title: string;
  detail: string;
  retryHref?: string;
}) {
  return (
    <div className="rounded-lg border border-dashed bg-card px-6 py-12 text-center" role="status">
      <h2 className="text-xl font-semibold text-foreground">{title}</h2>
      <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-muted-foreground">{detail}</p>
      {retryHref ? (
        <ButtonLink href={retryHref} className="mt-6" variant="outline">Try again</ButtonLink>
      ) : null}
    </div>
  );
}
