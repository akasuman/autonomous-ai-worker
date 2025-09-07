
import Image from "next/image";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

interface ResultCardProps {
  title: string;
  description: string;
  url: string;
  imageUrl?: string;
  summary?: string;
  topics?: string; // Add topics to the props
}

// Helper function to strip HTML tags
function stripHtml(html: string) {
  const doc = new DOMParser().parseFromString(html, 'text/html');
  return doc.body.textContent || "";
}

export default function ResultCard({ title, description, url, imageUrl, summary, topics }: ResultCardProps) {
  const cleanDescription = stripHtml(description); // Clean the description

  return (
    <Card className="flex flex-col h-full bg-gray-900 border-gray-700 text-white">
      <CardHeader>
        <CardTitle className="text-lg font-semibold line-clamp-2">{title}</CardTitle>
        {imageUrl && (
          <div className="relative w-full h-48 mt-2 rounded-md overflow-hidden">
            <Image
              src={imageUrl}
              alt={title}
              layout="fill"
              objectFit="cover"
              className="rounded-md"
            />
          </div>
        )}
      </CardHeader>
      <CardContent className="flex-grow">
        <CardDescription className="text-gray-400 line-clamp-4 mb-2">
          {cleanDescription}
        </CardDescription>
        {summary && (
          <div className="mt-4 p-2 bg-gray-800 rounded-md text-sm text-gray-300">
            <h4 className="font-semibold mb-1">AI Summary:</h4>
            <p className="line-clamp-3">{summary}</p>
          </div>
        )}
      </CardContent>
      <CardFooter className="flex flex-col items-start p-4 border-t border-gray-800">
        {topics && (
          <div className="text-xs text-gray-400 mb-2">
            <h4 className="font-semibold text-gray-300">Topics:</h4>
            <div className="flex flex-wrap gap-1 mt-1">
              {topics.split(',').map((topic, index) => (
                <span key={index} className="bg-gray-700 text-gray-200 px-2 py-0.5 rounded-full text-xs">
                  {topic.trim()}
                </span>
              ))}
            </div>
          </div>
        )}
        <a href={url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline text-sm mt-2">
          Read More
        </a>
      </CardFooter>
    </Card>
  );
}
