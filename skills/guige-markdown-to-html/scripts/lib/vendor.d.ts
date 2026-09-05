declare module "juice" {
  export interface Options {
    removeStyleTags?: boolean;
    preserveMediaQueries?: boolean;
  }

  export default function juice(html: string, options?: Options): string;
}

declare module "markdown-it-task-lists" {
  import type MarkdownIt from "markdown-it";

  interface TaskListOptions {
    enabled?: boolean;
    label?: boolean;
    labelAfter?: boolean;
  }

  export default function taskLists(md: MarkdownIt, options?: TaskListOptions): void;
}
