
// import SearchBar from "material-ui-search-bar";
import { OnSearchStateChange, SearchStates } from "../../types/search";

import { SearchBar } from './SearchBar'

interface Props {
  searchStates: SearchStates
  onSearchStateChange: OnSearchStateChange
}

export const Search = ({ searchStates, ...props }: Props) => {

  return (
    <div>
      {searchStates.map(
        (searchState, index) =>
          <SearchBar
            key={index}
            index={index}
            text={searchState}
            {...props}
          />
      )}
    </div>
  )
}
