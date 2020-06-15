# resolve the no GPU within docker container for tf-embed service

- [ ] https://stackoverflow.com/questions/59499764/tensorflow-not-tensorflow-gpu-failed-call-to-cuinit-unknown-error-303

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