import multiprocessing
import dill


def parallel_map(n_processes, fn, args_list):
    """A wrapper for Pool.map which can take unpicklable functions, using dill.

    `args_list` must be a list of `(args, kwargs)` tuples. If no keyword
    arguments are desired, an empty dictionary should be used.
    """
    dilled_requests = [dill.dumps([fn, (args, kwargs)])
                       for (args, kwargs) in args_list]
    pool = multiprocessing.Pool(n_processes)
    dilled_results = pool.map(undill_then_execute_and_redill, dilled_requests)
    pool.close();  pool.join()
    return [dill.loads(dr) for dr in dilled_results]


def undill_then_execute_and_redill(dilled_request):
    fn, (args, kwargs) = dill.loads(dilled_request)
    return dill.dumps(fn(*args, **kwargs))
