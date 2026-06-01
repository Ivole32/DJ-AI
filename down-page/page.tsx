import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Service Discontinued",
  description:
    "This service has been permanently discontinued and is no longer maintained. Official links and contact information are available below.",
  robots: {
    index: true,
    follow: true,
  },
  openGraph: {
    title: "Service Discontinued",
    description:
      "This service has been permanently discontinued and is no longer maintained.",
    type: "website",
  },
  twitter: {
    card: "summary",
    title: "Service Discontinued",
    description:
      "This service has been permanently discontinued and is no longer maintained.",
  },
};

const socialLinks = [
  {
    name: "GitHub",
    href: "https://github.com/ivole32",
  },
  {
    name: "X / Twitter",
    href: "https://x.com/ivole32",
  },
];

export default function DownPage() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    name: "Service Discontinued",
    description:
      "This service has been permanently discontinued and is no longer maintained.",
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLd),
        }}
      />

      <main className="min-h-screen bg-black text-white flex items-center justify-center px-6">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.08),transparent_65%)]" />

        <section className="relative w-full max-w-3xl rounded-3xl border border-white/10 bg-white/5 backdrop-blur-xl p-10 md:p-16 text-center">
          <div className="mb-6 inline-flex rounded-full border border-white/10 px-4 py-2 text-xs uppercase tracking-[0.3em] text-white/60">
            Service Status
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight">
            Service Discontinued
          </h1>

          <p className="mt-8 text-lg text-white/80 leading-8">
            This service has been permanently discontinued and is no longer
            actively maintained.
          </p>

          <p className="mt-4 text-white/50 leading-7">
            Thank you to everyone who supported, contributed to, and used this
            project.
          </p>

          <div className="mt-10 flex flex-wrap justify-center gap-3">
            {socialLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-xl border border-white/10 bg-white/[0.03] px-5 py-3 transition hover:bg-white/[0.08] hover:border-white/20"
              >
                {link.name}
              </a>
            ))}
          </div>

          <div className="mt-10">
            <a
              href="https://example.com/privacy"
              target="_blank"
              rel="noopener noreferrer"
              className="text-white/60 hover:text-white transition"
            >
              Privacy Policy
            </a>
          </div>
        </section>
      </main>
    </>
  );
}