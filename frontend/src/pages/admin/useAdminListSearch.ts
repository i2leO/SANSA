import { useSearchParams } from 'react-router-dom';

export default function useAdminListSearch() {
  const [searchParams, setSearchParams] = useSearchParams();
  const search = searchParams.get('q') || '';
  const setSearch = (value: string) => {
    setSearchParams(previous => {
      const next = new URLSearchParams(previous);
      if (value.trim()) next.set('q', value);
      else next.delete('q');
      return next;
    }, { replace: true });
  };
  return [search, setSearch] as const;
}
