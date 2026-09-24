import { Button } from "@/components/ui/button";
export default function Home() {
  return (
    <main className="min-h-screen bg-background flex flex-col items-center justify-center p-8">
      <div className="max-w-2xl w-full text-center space-y-6">
        {/*logo/Title*/}
        <div className="space-y-2">
          <h1 className="text-5xl font-bold tracking-tight">
            Docu<span className="text-primary">Mind</span>
          </h1>
          <p className="text-muted-foreground text-lg">
            AI-powered multimodal document intelligence platform.
          </p>
        </div>
        {/*Action Buttons */}
        <div className="flex gap-4 justify-center pt-4">
          <Button size="lg">
            Get Started
          </Button>
          <Button variant="outline" size="lg">
            View Docs
          </Button>
        </div>
        {/*Stack info*/}
        <div className="pt-8 grid grid-cols-3 gap-4 text-sm text-muted-foreground">
          <div className="p-3 rounded-lg bg-muted">
            <div className="font-medium text-foreground">Frontend</div>
            <div>Next.js+Typescript</div>
          </div>
          <div className="p-3 rounded-lg bg-muted">
            <div className="font-medium text-foreground">Backend</div>
            <div>FastAPI+Python</div>
          </div>
          <div className="p-3 rounded-lg bg-muted">
            <div className="font-medium text-foreground">AI Layer</div>
            <div>NLP+RAG+Agents</div>
          </div>
        </div>
      </div>
    </main>
  );
}