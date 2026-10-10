const paths: Record<string, string> = {
  home: 'm3 10 9-7 9 7M5 9v12h14V9M9 21v-8h6v8',
  respondents: 'M16 21v-3a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v3M22 21v-3a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75M13 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0',
  exports: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6v6h6M12 11v7m-3-3 3 3 3-3',
  knowledge: 'M12 5C8 2 4 3 2 4v16c3-1 6-1 10 1 4-2 7-2 10-1V4c-2-1-6-2-10 1v16',
  facilities: 'M4 22V4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v18M2 22h20M9 22v-5h6v5M8 6h1m6 0h1M8 10h1m6 0h1M8 14h1m6 0h1',
  scoring: 'M5 3h14v18H5zM8 7h8M8 11h1m6 0h1M8 15h1m6 0h1',
  users: 'M20 21v-2a7 7 0 0 0-14 0v2zM17 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0',
};
export default function AdminIcon({ name }: { name: string }) {
  return <svg aria-hidden="true" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><path d={paths[name] || paths.home} /></svg>;
}
