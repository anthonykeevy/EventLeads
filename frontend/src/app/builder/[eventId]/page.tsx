import dynamic from "next/dynamic";

const BuilderShell = dynamic(() => import("@/components/builder/BuilderShell"), {
  ssr: false,
});

export default function BuilderPage({ params }: { params: { eventId: string } }) {
  return <BuilderShell eventId={params.eventId} />;
}


