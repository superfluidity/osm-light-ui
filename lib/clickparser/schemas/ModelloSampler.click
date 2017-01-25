//
// sample packets between eth2 and eth1 at 20000 packets per second. send
// sampled packets up to linux device "sampler", created by FromHost.
// This configuration will only run in the kernel (so you must use
// 'click-install sampler.click').
//

elementclass RatedSampler {
// $rate |
  input -> rs :: RatedSplitter($rate);
  rs [0] -> t :: Tee;
  t [0] -> [0] output;
};

elementclass RatedSampler2 {
// $rate |
  input -> rs :: RatedSplitter($rate);
  rs [0] -> [0] output;
  rs [1] -> t :: Tee;
  t [0] -> s4 :: RatedSampler(20000);
  s4 [0] -> [0] output;		  
};


PollDevice(eth1) -> s1 :: RatedSampler2(20000);
s1 [0] -> Queue -> ToDevice(eth2);

