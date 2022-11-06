import { useEffect } from 'react';
import { useImmer } from "use-immer";
import { getPapers, getSemanticallySimilarPapersbyText, getSuggestedCategories } from '../api';
import { Card } from "./Card"

import {
  OutlinedInput,
  InputLabel,
  MenuItem,
  FormControl,
  ListItemText,
  Button,
  Checkbox,
  Tooltip,
  Select,
  SelectChangeEvent,
  CircularProgress
} from '@mui/material';


import { SearchStates } from '../types/search';
import { Search } from '../components/Search';
import { AddItemButton } from '../ui/AddItemButton';

import { useSearchParams } from 'react-router-dom';
import { ensureArray, getArrayParam, parseURLSearchParams } from '../utils/query_string';
import { CATEGORY_FILTER_OPTIONS, YEAR_FILTER_OPTIONS } from '../constants/search_filter';
import { useDebounce } from '../hooks/useDebounce';
import { SuggestedCategories } from '../components/Search/SuggestedCategories';
import { LoadingButton } from '../ui/LoadingButton';

export const Home = () => {
  const [urlParams, setUrlParams] = useSearchParams();

  const parsed_params = parseURLSearchParams(urlParams)

  const [papers, setPapers] = useImmer<any[]>([]);
  const [isLoadingPapers, setIsLoadingPapers] = useImmer<boolean>(false);
  const [categories, setCategories] = useImmer<string[]>(getArrayParam(parsed_params, 'categories', []));
  const [years, setYears] = useImmer<string[]>(getArrayParam(parsed_params, 'years', []));
  const [searchStates, setSearchStates] = useImmer<SearchStates>(getArrayParam(parsed_params, 'searchStates', ['']));
  const [total, setTotal] = useImmer<number>(0);
  const [error, setError] = useImmer<string>('');
  const [skip, setSkip] = useImmer(0);
  const [limit, setLimit] = useImmer(15);

  const [suggestedCategories, setSuggestedCategories] = useImmer<string[]>([]);

  const changeSuggestedCategories = async () => {
    const newSuggestedCategories = await getSuggestedCategories(searchStates)

    setSuggestedCategories(newSuggestedCategories)
  }
  const changeSuggestedCategoriesDebounced = useDebounce(changeSuggestedCategories, 800)

  const ITEM_HEIGHT = 48;
  const ITEM_PADDING_TOP = 8;
  const MenuProps = {
    PaperProps: {
      style: {
        maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
        width: 150,
      },
    },
  };

  useEffect(() => {
    setUrlParams({
      years,
      categories,
      searchStates
    })
  }, [years, categories, searchStates, setUrlParams])

  const handleYearSelection = (event: SelectChangeEvent<typeof years>) => {
    const {
      target: { value },
    } = event;
    setYears(
      // On autofill we get a stringified value.
      typeof value === 'string' ? value.split(',') : value,
    );
    setSkip(0)
  };

  const handleCatSelection = (event: SelectChangeEvent<typeof categories>) => {
    const {
      target: { value },
    } = event;
    setCategories(
      // On autofill we get a stringified value.
      typeof value === 'string' ? value.split(',') : value,
    );
    setSkip(0)
  };

  const handleSearchChange = (index: number, newText: string) => {
    setSearchStates(searchStates => {
      searchStates[index] = newText
    })

    changeSuggestedCategoriesDebounced()
  }

  const handleSearchItemAdd = () => {
    setSearchStates(searchStates => {
      searchStates.push('')
    })
  }

  const handleSearchItemRemove = (index: number) => {
    setSearchStates(searchStates => {
      searchStates.splice(index, 1)
    })
  }

  const queryPapers = async () => {
    setIsLoadingPapers(true)
    try {
      if (searchStates) {
        const result = await getSemanticallySimilarPapersbyText(searchStates, years, categories)
        setPapers(result.papers)
        setTotal(result.total)
      } else {
        setSkip(skip + limit);
        const result = await getPapers(limit, skip, years, categories);
        setPapers(result.papers)
        setTotal(result.total)
      }
    } catch (err) {
      setError(String(err));
    } finally {
      setIsLoadingPapers(false)
    }
  };

  // Execute this one when the component loads up
  useEffect(() => {
    queryPapers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const applySuggestedCategories = () => {
    setCategories(suggestedCategories)
  }

  return (
    <>
      <main role="main">
        <section className="jumbotron text-center bg-white" style={{ paddingTop: '40px' }}>
          <div className="container">
            <h1 className="jumbotron-heading">arXiv Paper Search</h1>
            <p className="lead text-muted">
              This demo uses the built in Vector Search capabilities of Redis Enterprise
              to show how unstructured data, such as paper abstracts (text), can be used to create a powerful
              search engine.
            </p>
            <p className="lead text-muted">
              <strong>Enter a search query below to discover scholarly papers hosted by <a href="https://arxiv.org/" target="_blank" rel="noreferrer">arXiv</a> (Cornell University).</strong>
            </p>
            <div className="container pb-4">
              <div style={{ display: 'flex', flexWrap: 'wrap' }}>
                <FormControl sx={{ width: 150, mr: 1, mt: 1 }}>
                  <InputLabel id="demo-multiple-checkbox-label">Year (either)</InputLabel>
                  <Select
                    labelId="demo-multiple-checkbox-label"
                    id="demo-multiple-checkbox"
                    multiple
                    value={years}
                    onChange={handleYearSelection}
                    input={<OutlinedInput label="Tag" />}
                    renderValue={(selected) => selected.join(', ')}
                    MenuProps={MenuProps}
                  >
                    {YEAR_FILTER_OPTIONS.map((year) => (
                      <MenuItem key={year} value={year}>
                        <Checkbox checked={years.indexOf(year) > -1} />
                        <ListItemText primary={year} />
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <FormControl sx={{ m: 0, width: '100%', mt: 1 }}>
                  <InputLabel id="demo-multiple-checkbox-label">Categories (exact match)</InputLabel>
                  <Select
                    labelId="demo-multiple-checkbox-label"
                    id="demo-multiple-checkbox"
                    multiple
                    value={categories}
                    onChange={handleCatSelection}
                    input={<OutlinedInput label="Category" />}
                    renderValue={(selected) => selected.join(', ')}
                    MenuProps={MenuProps}
                  >
                    {Object.entries(CATEGORY_FILTER_OPTIONS).map(([slug, name]) => (
                      <MenuItem key={slug} value={slug}>
                        <Checkbox checked={categories.indexOf(slug) > -1} />
                        <ListItemText primary={`${slug} (${name})`} />
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </div>

              <Search
                searchStates={searchStates}
                onSearchStateChange={handleSearchChange}
                onSearchItemRemove={handleSearchItemRemove}
              />

              <AddItemButton text="Add another article" onClick={handleSearchItemAdd} />

              <div className="pt-4">
                <LoadingButton loading={isLoadingPapers} onClick={queryPapers}> Search!</LoadingButton>
              </div>

              <SuggestedCategories
                options={suggestedCategories}
                onClick={applySuggestedCategories}
              />
            </div>

          </div>
        </section>
        <div className="album py-5 bg-light">
          <div className="container">
            <p style={{ fontSize: 15 }}>
              <Tooltip title="Filtered paper count" arrow>
                <em>{total} searchable arXiv papers</em>
              </Tooltip>
            </p>
          </div>
          <div className="container">
            {papers && (
              <div className="row">
                {papers.map((paper) => (
                  <Card
                    key={paper.pk}
                    title={paper.title}
                    authors={paper.authors}
                    paperId={paper.paper_id}
                    numPapers={15}
                    paperCat={paper.categories}
                    paperYear={paper.year}
                    categories={categories}
                    years={years}
                    similarity_score={paper.similarity_score}
                    setState={setPapers}
                    setTotal={setTotal}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </>
  );
};
