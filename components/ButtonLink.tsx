import Link, { type LinkProps } from "next/link";
import type { AnchorHTMLAttributes, ReactNode } from "react";
import { buttonStyles, type ButtonSize, type ButtonVariant } from "@/components/Button";

type ButtonLinkProps = LinkProps &
  Omit<AnchorHTMLAttributes<HTMLAnchorElement>, keyof LinkProps> & {
    children: ReactNode;
    size?: ButtonSize;
    variant?: ButtonVariant;
  };

export default function ButtonLink({
  children,
  className,
  size,
  variant,
  ...props
}: ButtonLinkProps) {
  return (
    <Link className={buttonStyles({ size, variant, className })} {...props}>
      {children}
    </Link>
  );
}
