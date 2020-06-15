# resolve the no GPU within docker container for tf-embed service

- [ ] https://stackoverflow.com/questions/59499764/tensorflow-not-tensorflow-gpu-failed-call-to-cuinit-unknown-error-303

<details>

```
2020-06-14 18:58:56,180  [DEBUG]               <module>()  ----------
MODULE_URL: https://tfhub.dev/google/universal-sentence-encoder/4

2020-06-14 18:58:56,198  [DEBUG]       initialize_model()  ----------

	downloading model... (this will take a minute)


INFO:absl:Using /tmp/tfhub_modules to cache modules.
2020-06-14 18:58:56.403652: W tensorflow/stream_executor/platform/default/dso_loader.cc:55] Could not load dynamic library 'libcuda.so.1'; dlerror: libcuda.so.1: cannot open shared object file: No such file or directory
2020-06-14 18:58:56.403706: E tensorflow/stream_executor/cuda/cuda_driver.cc:313] failed call to cuInit: UNKNOWN ERROR (303)
2020-06-14 18:58:56.403760: I tensorflow/stream_executor/cuda/cuda_diagnostics.cc:163] no NVIDIA GPU device is present: /dev/nvidia0 does not exist
2020-06-14 18:58:56.404178: I tensorflow/core/platform/cpu_feature_guard.cc:143] Your CPU supports instructions that this TensorFlow binary was not compiled to use: AVX2 FMA
2020-06-14 18:58:56.412448: I tensorflow/core/platform/profile_utils/cpu_utils.cc:102] CPU Frequency: 2200000000 Hz
2020-06-14 18:58:56.413226: I tensorflow/compiler/xla/service/service.cc:168] XLA service 0x7fdb18000b20 initialized for platform Host (this does not guarantee that XLA will be used). Devices:
2020-06-14 18:58:56.413264: I tensorflow/compiler/xla/service/service.cc:176]   StreamExecutor device (0): Host, Default Version
2020-06-14 18:59:02,219  [DEBUG]       initialize_model()  ----------
done!

DEBUG:log_utils:----------
done!
```

</details>



# resolve the tfhub download caching / file lock

1. one solution could be to have a separate `model-downloader-service` that shares a volume with anyone that needs tfhub models because it seems like the issue occurs when I `./restart`. That `model-downloader-service` would be a sinlge node. 

2. another solution could be to download during `docker build` -- that way we can rely on docker to cache for us rather than tensorflow at runtime. This solution kind of makes more sense since the model does not change much at runtime.

3. ...

<details>

```
2020-06-15 16:45:49,615  [DEBUG]       initialize_model()  ----------

        downloading model... (this will take a minute)


INFO:absl:Using /tmp/tfhub_modules to cache modules.
INFO:absl:Module 'https://tfhub.dev/google/universal-sentence-encoder/4' already being downloaded by '6c69899ff4c6.1.2edb12956e9e4e90be8b75fb5b3327fc'. Waiting.
INFO:absl:Module 'https://tfhub.dev/google/universal-sentence-encoder/4' already being downloaded by '6c69899ff4c6.1.2edb12956e9e4e90be8b75fb5b3327fc'. Waiting.
INFO:absl:Module 'https://tfhub.dev/google/universal-sentence-encoder/4' already being downloaded by '6c69899ff4c6.1.2edb12956e9e4e90be8b75fb5b3327fc'. Waiting.
INFO:absl:Module 'https://tfhub.dev/google/universal-sentence-encoder/4' already being downloaded by '6c69899ff4c6.1.2edb12956e9e4e90be8b75fb5b3327fc'. Waiting.
^C
```

</details>



### okay so... implemented `#2` but now a `connection reset by peer` may happen
### solution is to just build again

<details>

```
2020-06-15 17:29:48,120  [INFO ]       initialize_model()  ----------

        downloading model... (this will take a minute)


INFO:absl:Using /tmp/tfhub_modules to cache modules.
INFO:absl:Downloading TF-Hub Module 'https://tfhub.dev/google/universal-sentence-encoder-large/5'.
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/app/model_utils.py", line 57, in get_tfhub_sent_encoder
    return get_tfhub_sent_encoder_transformer()
  File "/app/model_utils.py", line 49, in get_tfhub_sent_encoder_transformer
    return initialize_model(url)
  File "/app/model_utils.py", line 33, in initialize_model
    model = hub.load(module_url)
  File "/usr/local/lib/python3.6/site-packages/tensorflow_hub/module_v2.py", line 97, in load
    module_path = resolve(handle)
  File "/usr/local/lib/python3.6/site-packages/tensorflow_hub/module_v2.py", line 53, in resolve
    return registry.resolver(handle)
  File "/usr/local/lib/python3.6/site-packages/tensorflow_hub/registry.py", line 42, in __call__
    return impl(*args, **kwargs)
  File "/usr/local/lib/python3.6/site-packages/tensorflow_hub/compressed_module_resolver.py", line 88, in __call__
    self._lock_file_timeout_sec())
  File "/usr/local/lib/python3.6/site-packages/tensorflow_hub/resolver.py", line 415, in atomic_download
    download_fn(handle, tmp_dir)
  File "/usr/local/lib/python3.6/site-packages/tensorflow_hub/compressed_module_resolver.py", line 85, in download
    response, tmp_dir)
  File "/usr/local/lib/python3.6/site-packages/tensorflow_hub/resolver.py", line 175, in download_and_uncompress
    self._extract_file(tgz, tarinfo, abs_target_path)
  File "/usr/local/lib/python3.6/site-packages/tensorflow_hub/resolver.py", line 151, in _extract_file
    buf = src.read(buffer_size)
  File "/usr/local/lib/python3.6/tarfile.py", line 708, in readinto
    buf = self.read(len(b))
  File "/usr/local/lib/python3.6/tarfile.py", line 697, in read
    b = self.fileobj.read(length)
  File "/usr/local/lib/python3.6/tarfile.py", line 539, in read
    buf = self._read(size)
  File "/usr/local/lib/python3.6/tarfile.py", line 552, in _read
    buf = self.__read(self.bufsize)
  File "/usr/local/lib/python3.6/tarfile.py", line 572, in __read
    buf = self.fileobj.read(self.bufsize)
  File "/usr/local/lib/python3.6/http/client.py", line 459, in read
    n = self.readinto(b)
  File "/usr/local/lib/python3.6/http/client.py", line 503, in readinto
    n = self.fp.readinto(b)
  File "/usr/local/lib/python3.6/socket.py", line 586, in readinto
    return self._sock.recv_into(b)
  File "/usr/local/lib/python3.6/ssl.py", line 1012, in recv_into
    return self.read(nbytes, buffer)
  File "/usr/local/lib/python3.6/ssl.py", line 874, in read
    return self._sslobj.read(len, buffer)
  File "/usr/local/lib/python3.6/ssl.py", line 631, in read
    v = self._sslobj.read(len, buffer)
ConnectionResetError: [Errno 104] Connection reset by peer
ERROR: Service 'nimbus-elastic-tf-embed-worker' failed to build: The command '/bin/sh -c python -c "from model_utils import get_tfhub_sent_encoder; get_tfhub_sent_encoder()"' returned a non-zero code: 1
```

</details>

# document the following


## Kibana is cool
https://www.elastic.co/kibana

## delete default_index

### https://www.elastic.co/guide/en/elasticsearch/reference/7.7/indices-delete-index.html

```
DELETE /default_index
```

## create default_index

### https://www.elastic.co/guide/en/elasticsearch/reference/7.7/indices-create-index.html

```
PUT /default_index
```

## set mappings on the default_index

### https://www.elastic.co/guide/en/elasticsearch/reference/7.7/mapping.html

### https://www.elastic.co/guide/en/elasticsearch/reference/7.7/removal-of-types.html

```
PUT /default_index/_mappings
{
    "properties": {
        "name": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "classification": {
            "type": "text"
        },
        "text": {
            "type": "text"
        },
        "embedding": {
            "type": "dense_vector",
            "dims": 512
        }
    }
}
```

## add a new thing into the default_index

### https://www.elastic.co/guide/en/elasticsearch/reference/7.7/docs-index_.html

```
POST /default_index/_doc
{
    "name" : "plato",
    "classification": "sentence",
    "text" : "I am plato."
}
```

## add a new thing into the default_index

### https://www.elastic.co/guide/en/elasticsearch/reference/7.7/docs-index_.html

```
POST /default_index/_doc
{
    "ok" : "plato",
    "wow" : "I can add any keys, so, what is the mapping for really?"
}
```

### and another

```
POST /default_index/_doc
{
    "ok" : "plato",
    "wow" : "will this sentence show first in the search because of the keyword search?"
}
```


# get schema information about the default_index
```
GET /default_index/
```


## searches the default_index in a Google-like way

### https://www.elastic.co/guide/en/elasticsearch/reference/7.7/search-search.html

```
GET /default_index/_search
{
    "query": {
        "simple_query_string": {
            "query": "hello search",
            "fields": []
        }
    }
}
```

## searches everything on default_index

### https://www.elastic.co/guide/en/elasticsearch/reference/7.7/search-search.html

```
GET /default_index/_search
{
    "query": {
        "match_all": {}
    }
}
```



# refresh
# https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-refresh.html
```
GET /default_index/_refresh
```


```
GET /non_exist_index/_refresh
```



## searches everything

### https://www.elastic.co/guide/en/elasticsearch/reference/7.7/search-search.html

```
GET _search
{
    "query": {
        "match_all": {}
    }
}
```
